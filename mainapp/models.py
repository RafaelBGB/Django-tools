from django.db import models
from django.db import transaction


class ProductCategory(models.Model):
    name = models.CharField(verbose_name='имя', max_length=64, unique=True)
    description = models.TextField(verbose_name='описание', blank=True)
    is_active = models.BooleanField(verbose_name='активна', db_index=True, default=True)

    def __str__(self):
        return self.name

    @transaction.atomic()
    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save(using=using)
        # self.category.delete()


class ProductQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        for item in self:
            item.delete()


class Product(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='category')
    name = models.CharField(verbose_name='имя продукта', max_length=128)
    image = models.ImageField(upload_to='products_images', blank=True)
    short_desc = models.CharField(verbose_name='краткое описание продукта', max_length=60, blank=True)
    description = models.TextField(verbose_name='описание продукта', blank=True)
    price = models.DecimalField(verbose_name='цена продукта', max_digits=8, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(verbose_name='количество на складе', default=0)
    is_active = models.BooleanField(verbose_name='активна', db_index=True, default=True)

    objects = ProductQuerySet.as_manager()

    def __str__(self):
        return f'{self.name} ({self.category.name})'

    @classmethod
    def get_items(cls):
        return cls.objects.select_related('category').\
            filter(is_active=True, category__is_active=True).\
            order_by('category', 'name')

    def delete(self, using=None, keep_parents=False):
        self.is_active = False
        self.save(using=using)
