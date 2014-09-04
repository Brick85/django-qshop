from django.core.management.base import BaseCommand
from optparse import make_option
from sitemenu.sitemenu_settings import MENUCLASS
from sitemenu import import_item
from django.utils.text import slugify
Menu = import_item(MENUCLASS)
from transliterate import translit
from django.utils import translation
from faker import Factory
fake = Factory.create()
import random
from qshop.models import Product, ProductImage
# pip install transliterate
# pip install fake-factory
import os
from django.conf import settings

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-c", "--count", dest="product_count", help="How many products to be generated", metavar="COUNT"),
    )

    def handle(self, *args, **options):
        translation.activate('ru')
        if not options['product_count']:
            self.stdout.write("Products count not entered!")
            self.stdout.write("--count [int]")
            return


        pcount = int(options['product_count'])

        categories = Menu.objects.filter(page_type="prod")
        # print len(categories) * 50
        # return
        # pcount = len(categories) * 50


        print "getting list of files..."
        mypath = os.path.join(settings.MEDIA_ROOT, 'dummy')
        onlyfiles = [ "dummy/"+f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath,f)) ]
        print "creating objects..."
        for i in range(pcount):
            # print fake.text(25)
            p = Product()
            name = fake.text(25)
            desc = fake.text(250)

            p.parameters_set_id = 1

            p.name = name
            p.name_ru = name
            p.name_en = name
            p.articul = slugify(name)
            p.price = random.randint(10, 10000)
            p.weight = random.randint(100, 10000)

            p.description = desc
            p.description_ru = desc
            p.description_en = desc

            p.image = random.choice(onlyfiles)

            p.save()

            for j in range(random.randint(0, 4)):
                pi = ProductImage()
                pi.product = p
                pi.image = random.choice(onlyfiles)
                pi.save()

            for j in range(random.choice([1,1,1,1,2,2,3])):
                p.category.add(random.choice(categories))

            print "created product", i
