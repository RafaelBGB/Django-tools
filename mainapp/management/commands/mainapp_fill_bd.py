from django.core.management.base import BaseCommand
from mainapp.models import Product, ProductCategory
import json
from authapp.models import ShopUser

JSON_PATH = 'mainapp/json'


def load_from_json(file_name):
    with open(file_name, encoding='utf-8') as infile:
        return json.load(infile)


class Command(BaseCommand):
    def handle(self, *args, **options):
        categories = load_from_json('mainapp/json/categories.json')

        ProductCategory.objects.all().delete()
        for category in categories:
            ProductCategory.objects.create(**category)

        products = load_from_json('mainapp/json/products.json')
        Product.objects.all().delete()
        for product in products:
            _category = ProductCategory.objects.get(name=product['category'])
            product['category'] = _category
            Product.objects.create(**product)

    if not ShopUser.objects.filter(username='django').exists():
        ShopUser.objects.create_superuser('django', 'django@geekshop.local',
                                          'geekbrains', age=33)
