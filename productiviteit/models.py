# encoding: utf-8

# Imports
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible


# Gegevens over Regios
@python_2_unicode_compatible
class Regio(models.Model):
    naam = models.CharField(max_length = 100, primary_key = True)
    # naam van het model, want Employee wordt pas later gemaakt
    regiomanager = models.ForeignKey('Employee', related_name='+', null = True)

    def __str__(self):
        return str(self.naam)


# Gegevens over Vestigingen
@python_2_unicode_compatible
class Vestiging(models.Model):

    naam = models.CharField(max_length = 100)
    # naam van het model, want Employee wordt pas later gemaakt
    teamleider = models.ForeignKey('Employee', related_name= 'teamleider', null = True)
    bij_regio = models.ForeignKey(Regio)

    def __str__(self):
        return str(self.naam)

    class Meta:
        verbose_name_plural = 'vestigingen'

# Gegevens over Functies
@python_2_unicode_compatible
class Functie(models.Model):
    naam = models.CharField(primary_key = True, max_length = 100)
    uren_dienstverband = models.IntegerField(default = 36)
    opleidingsdagen = models.DecimalField(max_digits = 5, decimal_places = 2)
    supervisie_krijgen = models.DecimalField(max_digits = 5, decimal_places = 2)
    werkbegeleiding_krijgen = models.DecimalField(max_digits = 5, decimal_places = 2)
    studieduur_krijgen = models.DecimalField(max_digits = 5, decimal_places = 2)
    werkoverleg = models.DecimalField(max_digits = 5, decimal_places = 2)
    meelezen_verslagen = models.DecimalField(max_digits = 5, decimal_places = 2)
    supervisie_geven = models.DecimalField(max_digits = 5, decimal_places = 2)
    werkbegeleiding_geven = models.DecimalField(max_digits = 5, decimal_places = 2)
    praktijkopleiding_geven = models.DecimalField(max_digits = 5, decimal_places = 2)
    teamleider_taken = models.DecimalField(max_digits = 5, decimal_places = 2)
    KP_werkzaamheden = models.DecimalField(max_digits = 5, decimal_places = 2)
    overig = models.DecimalField(max_digits = 5, decimal_places = 2)
    niet_benoemd = models.DecimalField(max_digits = 5, decimal_places = 2)
    vakantie = models.DecimalField(max_digits = 5, decimal_places = 2)
    levensloop = models.DecimalField(max_digits = 5, decimal_places = 2)

    def __str__(self):
        return str(self.naam)

# Gegevens over medewerkers
@python_2_unicode_compatible
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personeelsnummer = models.IntegerField()
    voornaam = models.CharField(max_length = 100)
    tussenvoegsels = models.CharField(max_length = 20, blank = True)
    achternaam = models.CharField(max_length = 100)
    vestiging = models.ForeignKey(Vestiging)
    functie = models.ForeignKey(Functie)
    fte = models.FloatField(default = 1)
    ADV = models.BooleanField(default = 0)

    def __str__(self):
        if self.tussenvoegsels == '':
            return ' '.join([self.voornaam, self.achternaam])
        else:
            return ' '.join([self.voornaam, self.tussenvoegsels, self.achternaam])

        # return self.achternaam


# Model naar export tabel AFAS
@python_2_unicode_compatible
class Timechart(models.Model):
    boekjaar = models.IntegerField(null= True)
    periode = models.IntegerField(null= True)
    nacalculatie = models.CharField(max_length = 100, blank = True, default = '')
    naam = models.CharField(max_length = 100, blank = True, default = '')
    personeelsnummer = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='timecharts')
    datum = models.DateField(null= True)
    aantal = models.DecimalField(max_digits=20, decimal_places=2, null= True)
    soort = models.CharField(max_length = 10, blank = True, default = '')
    code = models.CharField(max_length =  20, blank = True, default = '')
    kostendrager = models.CharField(max_length = 10, blank = True, default = '')
    jaar = models.IntegerField(null= True)
    maand = models.IntegerField(null= True)
    direct = models.CharField(max_length = 10, blank = True, default = '')

    def __str__(self):
        return str(self.naam)




# Model om individuele aanpassingen in beschikbare uren weer te geven
@python_2_unicode_compatible
class Planning(models.Model):

    PLANNING_KEUZES = (
    ('OLD', 'opleidingsdagen')
    ,('SV_K', 'supervisie krijgen')
    ,('WBG_K', 'werkbegeleiding krijgen')
    ,('SD_K', 'studieduur krijgen')
    ,('WO', 'werkoverleg')
    ,('MLV', 'meelezen verslag')
    ,('SV_G', 'supervisie geven')
    ,('WBG_G', 'werkbegeleiding_geven')
    ,('PO_G', 'praktijkopleiding geven')
    ,('TLT', 'taken teamleider')
    ,('KP', 'KP werkzaamheden')
    ,('OV', 'overig')
    ,('NB', 'niet benoemd'))

    medewerker = models.ForeignKey(Employee)
    soort = models.CharField(max_length = 5, choices = PLANNING_KEUZES, default = 'OV')
    startdatum = models.DateField()
    einddatum = models.DateField()
    hoeveelheid = models.DecimalField(max_digits = 5, decimal_places = 2, default = 0.0)

    def __str__(self):
        return str(self.soort)

    class Meta:
        verbose_name_plural = 'planningen'

class VerdeeldePlanning(models.Model):
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    datum = models.DateField()
    verdeling = models.DecimalField(max_digits = 5, decimal_places = 3, default = 0.0)
    def __str__(self):
        return str(self.planning)

    class Meta:
        verbose_name_plural = 'verdeeldeplanningen'

# Alleen een lijst van datums waarmee we berekeningen kunnen maken
class Dagen(models.Model):
    dag = models.DateField()

    def __str__(self):
        return str(self.dag)
    class Meta:
        verbose_name_plural = 'dagen'

# Lijst van feestdagen. Door gebruikers aan te vullen
class Feestdagen(models.Model):
    dag = models.ForeignKey(Dagen)
    vrije_dag = models.CharField(max_length = 100)

    def __str__(self):
        return str(self.dag)

    class Meta:
        verbose_name_plural = 'feestdagen'
