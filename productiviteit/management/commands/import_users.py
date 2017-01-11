# Imports
from django.core.management.base import BaseCommand, CommandError
from django.db import DatabaseError, IntegrityError
from django.contrib.auth.models import User
from productiviteit.models import Employee, Vestiging, Functie
import csv


class Command(BaseCommand):
    help = 'Importeerd gebruikers en daarmee verbonden medewerkers'

    def add_arguments(self, parser):
        parser.add_argument('pad', nargs='+', type=str)

    def handle(self, *args, **options):
        pad = options['pad'][0]

        count = 1

        with open(pad) as csvfile:
            linereader = csv.reader(csvfile, delimiter=',', quotechar='"')
            next(linereader)
            for row in linereader:

                # Beperking van het aantal rijen


                personeelsnummer = int(row[0])
                pers_id = row[1].strip()
                vestiging = row[2].strip()
                gebruikersnaam = row[3].strip()
                voornaam = row[4].strip()
                tussenvoegsel = row[5].strip()
                achternaam = row[6].strip()
                email = row[7].strip()
                wachtwoord = row[8].strip()

                print(vestiging)


                #  Voorvoegsels handelen
                if tussenvoegsel == '':
                    naam_vol = achternaam
                else:
                    naam_vol = ' '.join([tussenvoegsel, achternaam])


                # Vestiging uit de database ophalen
                v = Vestiging.objects.get(naam = vestiging)

                # Functie voor nu standaard op basispsycholoog
                f = Functie.objects.get(naam = 'Basispsycholoog')

                # gebruiker aanmaken
                try:
                    u = User.objects.create(username = gebruikersnaam,
                    password = wachtwoord, email = email, first_name = voornaam,
                    last_name = naam_vol)

                    e = Employee.objects.create(user = u,
                    personeelsnummer = personeelsnummer,
                    voornaam = voornaam,
                    achternaam = achternaam,
                    tussenvoegsels = tussenvoegsel,
                    vestiging = v,
                    functie = f)

                except DatabaseError as e:
                    self.stderr.write('there was a problem saving the user on line: ' + str(count)  + str(e.__cause__))


                count = count + 1
