from django.contrib import auth, messages
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.transaction import atomic
from django.db.models.signals import post_save
from django.shortcuts import render, HttpResponseRedirect
from django.urls import reverse

from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm, \
    ShopUserEditForm, ShopUserProfileChangeForm
from authapp.models import ShopUser, ShopUserProfile


def login(request):
    form = ShopUserLoginForm(data=request.POST)
    next = request.GET['next'] if 'next' in request.GET.keys() else ''
    print(next)
    if request.method == 'POST' and form.is_valid():
        username = request.POST.get('username')
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user and user.is_active:
            auth.login(request, user)
            if 'next' in request.POST.keys():
                return HttpResponseRedirect(request.POST['next'])
            else:
                return HttpResponseRedirect(reverse('main:index'))

    context = {
        'page_title': 'авторизация',
        'form': form,
        'next': next,
    }
    return render(request, 'authapp/login.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main:index'))


@atomic
def edit(request):
    if request.method == 'POST':
        form = ShopUserEditForm(request.POST, request.FILES,
                                instance=request.user)
        profile_form = ShopUserProfileChangeForm(request.POST, request.FILES,
                                                 instance=request.user.shopuserprofile)

        if form.is_valid() and profile_form.is_valid():
            form.save()
            profile_form.save()
            return HttpResponseRedirect(reverse('auth:edit'))
    else:
        form = ShopUserEditForm(instance=request.user)
        profile_form = ShopUserProfileChangeForm(instance=request.user.shopuserprofile)

    context = {
        'page_title': 'личный кабинет',
        'form': form,
        'profile_form': profile_form,
    }
    return render(request, 'authapp/edit.html', context)


def register(request):
    if request.method == 'POST':
        form = ShopUserRegisterForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.set_activation_key()
            user.save()
            user.send_confirm_email()
            messages.success(request, 'Вы успешно зарегистрированы. '
                                      'Для заверщения регистрации пройдите '
                                      'по ссылке из email.')
    else:
        form = ShopUserRegisterForm()

    context = {
        'page_title': 'регистрация',
        'form': form,
    }
    return render(request, 'authapp/register.html', context)


def verify(request, email, activation_key):
    user = get_user_model().objects.get(email=email)
    if user.activation_key == activation_key and not user.is_activation_key_expired():
        user.is_active = True
        user.save()
        auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return render(request, 'authapp/verification.html')


@receiver(post_save, sender=ShopUser)
def save_or_create_profile(sender, instance, created, **kwargs):
    if created:
        ShopUserProfile.objects.create(user=instance)
    else:
        instance.shopuserprofile.save()
