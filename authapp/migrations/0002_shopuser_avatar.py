# Generated by Django 3.2.9 on 2021-12-13 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shopuser',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='user_avatars'),
        ),
    ]
