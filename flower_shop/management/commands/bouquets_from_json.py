from django.core.management.base import BaseCommand
from django.core.files import File
from tempfile import NamedTemporaryFile
from catalog.models import Bouquet
import requests
import json


class Command(BaseCommand):
    help = 'Imports bouquets from JSON'

    def handle(self, *args, **options):
        with open('C:/Users/aszdo/PycharmProjects/Flowershop/flower_shop/bouquets.json', 'r', encoding='utf-8') as f:
            bouquets = json.load(f)

        for item in bouquets:
            bouquet = Bouquet(
                name=item['name'],
                consists=item['consists'],
                price=item['price']
            )

            if item['pic1']:
                with NamedTemporaryFile() as img_temp:
                    response = requests.get(item['pic1'])
                    img_temp.write(response.content)
                    img_temp.flush()
                    bouquet.pic1.save(f"{item['name']}_1.jpg", File(img_temp))

            if item['pic2']:
                with NamedTemporaryFile() as img_temp:
                    response = requests.get(item['pic2'])
                    img_temp.write(response.content)
                    img_temp.flush()
                    bouquet.pic2.save(f"{item['name']}_2.jpg", File(img_temp))

            bouquet.save()
