
# Script om eerste vulling van vestigingen en regios te doen


# Imports
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, IntegrityError
from productiviteit.models import Vestiging, Regio


class Command(BaseCommand):

    help = 'Maakt regios en bijhorende vestigingen aan in de DatabaseError'


    def handle(self, *args, **options):

        # dict met regios als keys en lijst met bijhorende
        # vestigingen als value
        regio_indeling = {
        'Amsterdam': ['Alkmaar', 'Amsterdam', 'Interapy', 'Zaandam'],
        'Arnhem': ['Arnhem', 'Doetinchem', 'Ede', 'Nijmegen', 'Nijmegen (Van Trieststraat)'],
        'Breda': ['Breda', 'Dordrecht', 'Goes'],
        'Den Bosch': ['Den Bosch', 'Eindhoven','Oss'],
        'Den Haag':	['Den Haag', 'Leiden', 'Zoetermeer'],
        'Groningen': ['Assen', 'Groningen', 'Leeuwarden'],
        'Maastricht': ['Heerlen', 'Maastricht'],
        'Rotterdam': ['Delft', 'Rotterdam'],
        'Utrecht': ['Amersfoort', 'HSK Expertise', 'Conversie', 'Utrecht'],
        'Zwolle': ['Hengelo', 'Hoogeveen', 'Zwolle'],
        'Onafhankelijk': ['Expertisecentrum Kinderen', 'Expertisecentrum Tics',
        'Hoofdkantoor', 'Medisch Centrum Kinderwens', 'SPV', 'ZZBewaren']
        }

        # over dict loopen en regio aanmaken en daarmee gekoppelde vestigingen
        for item in regio_indeling.keys():
             vestigingen = regio_indeling.get(item)
             try:
                 regio = Regio.objects.create(naam = item)
                 for vest in regio_indeling.get(item):
                     vestiging = Vestiging.objects.create(naam = vest, bij_regio = regio)
             except DatabaseError as e:
                self.stderr.write('there was a problem saving the region or one of its locations' + e.__cause__)
