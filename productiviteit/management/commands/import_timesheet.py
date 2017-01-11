
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

    def handle(self, *args, **options):
        pad = options['pad'][0]


        workbook = xlrd.open_workbook(pad)
        worksheet = workbook.sheet_by_name('Nacalculatieoverzicht (incl. au')

        # Change this depending on how many header rows are present
        # Set to 0 if you want to include the header data.
        offset = 3

        rows = []
        for i, row in enumerate(range(worksheet.nrows)):
            if i <= offset:  # (Optionally) skip headers
                continue
            r = []
            for j, col in enumerate(range(worksheet.ncols)):

                v_raw = worksheet.cell_value(i, j)

                # Bij positie bepalen
                integers = {0, 1, 4, 10, 11}
                strings = {2, 3, 7, 8, 9, 12}
                dates = {5}
                decimals = {6}
                if j in integers:
                    # print('converting to integer: ' + str(v_raw) + ' ' + str(i) + ':' + str(j))
                    v = int(v_raw)
                elif j in strings:
                    # print('converting to string: ' + str(v_raw))
                    v = str(v_raw)
                elif j in dates:
                    # print('converting to date: ' + str(v_raw))
                    v = xlrd.xldate.xldate_as_datetime(v_raw, workbook.datemode).strftime('%Y-%m-%d')
                elif j in decimals:
                    # print('converting to float: ' + str(v_raw))
                    v = Decimal(float(v_raw))

                r.append(v)
            rows.append(r)

        print('Got '  + str(len(rows)) + ' rows')
        print(rows[0])  # Print eerste rij met data
        # print(rows[offset])  # Print first data row sample


        # defaultdict gebruiken om in een dict per medewerker een
        # lijst van rijen te bouwen
        empdict = defaultdict(list)
        count = 1
        for row in rows:
            if count < 200000:
                empdict[row[4]].append(row)
                count = count + 1
            else:
                break


        # saving to database
        # check of medewerker in de database startdatum
        for key in empdict.keys():
            print('personeelsnummer: ' + str(key))
            if Employee.objects.filter(personeelsnummer = key).exists():
                werknemer = Employee.objects.get(personeelsnummer = key)
                activiteiten = empdict.get(key)

                # Lijst maken om timesheet objecten in op te slaan
                timesheets = list()
                for act in activiteiten:

                    print(str(act[6]))

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

                # Dan de hele lijst in 1 keer naar de database
                Timechart.objects.bulk_create(timesheets)



            else:
                print('personeelsnummer niet bekend: ' + str(key))






        # pp = pprint.PrettyPrinter(indent = 2)
        # pp.pprint(empdict)
