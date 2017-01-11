
# Imports
import datetime
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, IntegrityError
from productiviteit.models import Dagen


class Command(BaseCommand):
    help = 'maakt een lijst met datums vanaf 1 jan 2016 in de database'

    def handle(self, *args, **options):

        # startdatum
        base = datetime.datetime.strptime('01012016', '%d%m%Y').date()
        date_list = [base + datetime.timedelta(days=x) for x in range(0, 3650)]

        Dagen_object_list = []

        for date in date_list:
            Dagen_object_list.append(Dagen(dag = date))

        Dagen.objects.bulk_create(Dagen_object_list)














        # pp = pprint.PrettyPrinter(indent = 2)
        # pp.pprint(empdict)
