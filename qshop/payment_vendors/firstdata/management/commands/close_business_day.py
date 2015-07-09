# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from qshop.payment_vendors.firstdata import Firstdata


# Run from command line: manage.py close_business_day
class Command(BaseCommand):
    help = 'First data closure day return: RESULT: OK RESULT_CODE: 500 FLD_075: 4 FLD_076: 6 FLD_087: 40 FLD_088: 60'

    def handle(self, *args, **options):
        merchant = Firstdata(verbose=False)
        self.stdout.write('Firstdata business day closure result: "%s"' % merchant.close_day())
