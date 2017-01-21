
# Imports
import xlrd, pprint
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, IntegrityError
from django.contrib.auth.models import User
from productiviteit.models import Employee, Vestiging, Functie, Timechart
from decimal import Decimal



class Command(BaseCommand):
    help = 'Importeerd afas export in de database'

    def add_arguments(self, parser):
        parser.add_argument('pad', nargs='+', type=str)
        parser.add_argument('jaar', nargs='+', type=int)

    def handle(self, *args, **options):
        pad = options['pad'][0]
        jaar = options['jaar'][0]

        workbook = xlrd.open_workbook(pad)
        worksheet = workbook.sheet_by_name('Nacalculatieoverzicht (incl. au')

        # Bijhouden of we het inlezen kan beginnen
        skip = True

        headers = {'Bkjr.': {'type': 'integer'},
                    'Periode' : {'type': 'integer'},
                    'Nacalculatie' : {'type': 'string'},
                     'Naam' : {'type': 'string'},
                     'Mdw.' : {'type': 'integer'},
                     'Datum' : {'type': 'date'},
                     'Aantal' : {'type': 'decimal'},
                     'Srt.' : {'type': 'string'},
                     'Code' : {'type': 'string'},
                     'Kostendrager medewerker': {'type': 'string'},
                     'jaar': {'type': 'integer'},
                     'maand': {'type': 'integer'},
                     'direct' : {'type': 'string'}}
        types = []
        cols = []

        rows = []

        for i, row in enumerate(range(worksheet.nrows)):
        # for i, row in enumerate(range(0,500)):

            # Tot we de header rij hebben gevonden overslaan
            if skip:
                if worksheet.cell_value(i, 0) in headers.keys():
                    skip = False
                    # Maak een lijst met de header types in de volgorde zoals in bestand
                    for j, col in enumerate(range(worksheet.ncols)):
                        v = worksheet.cell_value(i, j)
                        cols.append(v)
                        types.append(headers[v]['type'])
                    continue
                else:
                    continue


            r = []
            for j, col in enumerate(range(worksheet.ncols)):

                v_raw = worksheet.cell_value(i, j)

                try:
                    # afhankelijk van type cell verwerken
                    if types[j] == 'integer':
                        v = int(v_raw)
                    elif types[j] == 'string':
                        v = str(v_raw)
                    elif types[j] == 'date':
                        v = xlrd.xldate.xldate_as_datetime(v_raw, workbook.datemode).date()
                    elif types[j] == 'decimal':
                        v = Decimal('% 6.2f' % v_raw)

                    r.append(v)
                except Exception as e:
                    print('row ' + str(j) + 'could not be processed due to the following error: ' + e.message)

            # Check of deze rij het jaar bevat dat is opgegeven
            if(r[cols.index('Datum')].year == jaar):
                rows.append(r)

        # defaultdict gebruiken om in een dict per medewerker een
        # lijst van rijen te bouwen
        empdict = defaultdict(list)
        for row in rows:
            empdict[row[4]].append(row)

        # saving to database
        # check of medewerker in de database startdatum
        for key in empdict.keys():
            # print('personeelsnummer: ' + str(key))
            if Employee.objects.filter(personeelsnummer = key).exists():
                werknemer = Employee.objects.get(personeelsnummer = key)
                activiteiten = empdict.get(key)

                # Lijst maken om timesheet objecten in op te slaan
                timesheets = list()
                for act in activiteiten:

                    try:
                        timesheets.append(Timechart(
                        boekjaar = act[0]
                        ,periode = act[1]
                        ,nacalculatie = act[2]
                        ,naam = act[3]
                        ,personeelsnummer = werknemer
                        ,datum = act[5]
                        ,aantal = act[6]
                        ,soort = act[7]
                        ,code = act[8]
                        ,kostendrager = act[9]
                        ,jaar = act[10]
                        ,maand = act[11]
                        ,direct = act[12]
                        ))
                    except Exception as e:
                        print('row could not saved as object because: ' + str(e.message))

                # oude entries van deze werknemen verwijderen
                oud = Timechart.objects.filter(personeelsnummer = werknemer, datum__year = jaar)
                if oud.exists():
                    oud.delete()

                # Dan de hele lijst nieuwe in 1 keer naar de database
                Timechart.objects.bulk_create(timesheets)
