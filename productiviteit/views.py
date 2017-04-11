from django.contrib.auth.views import login
from django.contrib import messages
from django.shortcuts import render, redirect, render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Planning, Employee, Dagen, Feestdagen, VerdeeldePlanning, Timechart, Vestiging
from .forms import PlanningForm
from django.contrib.auth.models import User
from django.forms import formset_factory, modelformset_factory
from django.db import IntegrityError, transaction
from django.db.models.functions import TruncMonth, TruncYear as Year
from django.db.models import Sum, Count, Value, Q
from django.core.urlresolvers import reverse
from django.http import JsonResponse
import datetime, time, pprint
from django.db.models import Prefetch
from productiviteit.utils import get_role, has_permission, lijst_jaren

pp = pprint.PrettyPrinter(indent=4)

"""
View met detailoverzicht van productiviteit afgelopen periode
"""
@login_required(login_url='/login/')
def behandelaar(request, medewerker_id=None):

    # als er een specifieke medewerker wordt gevraagd. Dan krijgt je die
    if medewerker_id:
        medewerker = get_object_or_404(Employee, pk = int(medewerker_id))
        rol = get_role(medewerker)

        # lijst met jaren maken, huidig jaar en 2 jaar ervoor
        jaren = lijst_jaren

    # als er geen specifieke medewerker is gevraagd, kijken of we uit de user
    # een mederwerker kunnen halen en daar naar redirecten
    else:
        medewerker = get_object_or_404(Employee, user = request.user)
        return redirect('/behandelaar/' + str(medewerker.pk) + '/')

    return render(request, 'productiviteit/home.html', {
    'naam': medewerker, 'jaren': jaren, 'rol': rol,
    'niveau': 'individueel', 'vestiging': rol['vestiging'],
    })


"""
View waarin planningen kunnen worden ingevoerd, of aangepast
"""
@login_required(login_url='/login/')
def planning(request, planning_id=None):

    medewerker = Employee.objects.get(user = request.user)
    if planning_id:
        # voor template, voor een edit willen we niet de knoppen tonen om meer
        # planningen aan te maken
        edit = True
        # Anders krijgen we een extra form in de set
        extra = 0
        qset = Planning.objects.filter(pk = planning_id)
    # Zonder planning_id wil iemand een nieuwe planning invoeren
    else:
        edit = False
        extra = 1
        qset = Planning.objects.none()

    # lege formset maken met formset_factory
    planning_formset = modelformset_factory(Planning, form = PlanningForm, extra = extra)
    # dan definitieve aanmaken met evt initiele data
    formset = planning_formset(queryset = qset, form_kwargs={'user': request.user})

    # ingevulde formulieren verwerken
    if request.method == 'POST':
        formset = planning_formset(request.POST, form_kwargs={'user': request.user})
        if formset.is_valid():

            verdelingen_to_save = []

            for planning in formset:
                soort = planning.cleaned_data.get('soort')
                startdatum = planning.cleaned_data.get('startdatum')
                einddatum = planning.cleaned_data.get('einddatum')
                hoeveelheid = planning.cleaned_data.get('hoeveelheid')

                if soort and startdatum and einddatum and hoeveelheid:

                    # werkdagen ophalen in de opgegegen periode
                    werkdagen = Dagen.objects.filter(dag__gte=startdatum, dag__lte=einddatum,
                    dag__week_day__in=[2,3,4,5,6]).exclude(feestdagen__vrije_dag__isnull = False)

                    if len(werkdagen) == 0:
                        print('geen werkdagen')
                        messages.error(request, "Er zijn geen werkdagen gevonden tussen " + str(startdatum) + " en " + str(einddatum))
                        return render(request, 'productiviteit/planning_create.html', {'planning_formset': formset})
                    else:
                        # Planningsobject maken/updaten
                        planning_to_save = planning.save(commit = False)
                        planning_to_save.medewerker = medewerker
                        planning_to_save.save()

                        # Verdeelde planningen opslaan/vervangen
                        if planning_to_save.verdeeldeplanning_set.all().exists():
                            planning_to_save.verdeeldeplanning_set.all().delete()

                        verdeelde_hoeveelheid = hoeveelheid / werkdagen.count()

                        for item in werkdagen:
                            werkdag = item.dag
                            verdelingen_to_save.append(VerdeeldePlanning(planning = planning_to_save,
                                datum = item.dag, verdeling = verdeelde_hoeveelheid))

                        VerdeeldePlanning.objects.bulk_create(verdelingen_to_save)

            return redirect(reverse('behandelaar'))


    return render(request, 'productiviteit/planning_create.html', {'planning_formset': formset, 'edit': edit})


"""
Ajax date view. Geeft data terug op een AJAX verzoek vanuit een
andere view.
"""
def ajax_data(request):

    def month_list(date):
        result=[]
        for i in range(0,12):
            if i == 0:
                date = date.replace(day=1)
                result.append(date)
            else:
                date = date - datetime.timedelta(days=1)
                date = date.replace(day=1)
                result.append(date)

        result = sorted(result)
        return result

    def get_value(search_list, key, key_value, key_result):
        dictio = next((item for item in search_list if item[key] == key_value), None)

        if dictio:
            return dictio.get(key_result)
        else:
            return 0

    if request.method == 'POST' and request.is_ajax():

        pk = request.POST.get('id')
        niveau = request.POST.get('niveau', 'individueel')
        doel = request.POST.get('doel', 'detail')
        if niveau == 'vestiging':
            vestiging = Vestiging.objects.get(pk = pk)
            med_lijst = vestiging.employee_set.values()
        elif niveau == 'individueel':
            med_lijst = Employee.objects.filter(pk = pk)

        # uit de keuze een start en einddatum berekenen
        try:
            keuze = int(request.POST.get('keuze', 0))
        except:
            print('Choice could not be coerced to an integer')

        # 1 is de code voor de laatste 12 maanden
        if keuze == 1:
            # Eind is de laatste dag van deze maand
            eind = datetime.datetime.today().date()
            eind = eind.replace(day=1) + datetime.timedelta(days=32)
            eind = eind.replace(day=1) - datetime.timedelta(days=1)
            start = month_list(eind)[0]
        # anders is er een jaar gekozen
        else:
            # print('keuze voor het jaar: ' + str(keuze))
            eind = datetime.datetime.strptime((str(keuze) + '1231'), '%Y%m%d').date()
            start = month_list(eind)[0]

        # Beschikbare uren door het aantal werkdagen te tellen en met 7,2 uur te vermenigvuldigen
        uren_b = Dagen.objects.filter(dag__week_day__in=[2,3,4,5,6], dag__gte=start, dag__lte=eind) \
            .exclude(feestdagen__vrije_dag__isnull = False) \
            .annotate(groep_maand = TruncMonth('dag')) \
            .values('groep_maand') \
            .annotate(beschikbaar = Count('dag') * 7.2) \
            .values('groep_maand', 'beschikbaar')


        # Alternatieve query, die meerdere resultaten tegelijk op kan halen

        # regels voor prefetch van afas uren (directe uren)
        p_afas = Prefetch('timecharts',
            queryset = Timechart.objects\
                        # .only('datum', 'direct', 'aantal')\
                        .filter(datum__gte=start, datum__lte=eind, direct='1.0')\
                        .annotate(groep_maand = TruncMonth('datum')))

        # regels voor prefetch ipp uren
        p_ipp = Prefetch('planning_set__verdeeldeplanning_set',
            queryset = VerdeeldePlanning.objects\
                        # .only('datum', 'verdeling')
                        .filter(datum__gte=start, datum__lte=eind) \
                        .annotate(groep_maand = TruncMonth('datum')))

        # gegevens ophalen van medewerkers, aangevuld met afas en ipp uren
        data_teamleden = Employee.objects.filter(pk__in = med_lijst.values_list('pk')).prefetch_related(p_afas, p_ipp)


        # afas en ipp prefetches verder verwerken
        totaal_afas = {}
        totaal_beschikbaar = {}

        teamleden = {}
        # Queryset heeft een lijst van medewerkers en bijhorende gegevens
        # opgeleverd. Afhankelijk van het doel, sommeren we op totaalniveau per maand
        # of maken we een samenvatting per medewerker, zonder maandonderscheid
        for teamlid in data_teamleden:

            # Naam van de behandelaar
            tl_naam = teamlid.__str__()
            # Pk van de behandelaar
            tl_pk = teamlid.pk

            #  Afas uren per maand uitrekenen
            timecharts = teamlid.timecharts\
                    .values('groep_maand')\
                    .annotate(uren_direct = Sum('aantal'))\
                    .values('groep_maand', 'uren_direct')

            # toevoegen aan dict
            teamleden[tl_naam] = {'timecharts': {x['groep_maand']: x['uren_direct'] for x in timecharts}}

            teamleden[tl_naam]['pk'] = tl_pk
            # Ipp planningen hebben 2 niveaus, de planning en de verdeelde planning, die meerdere
            # maanden kan bevatten. Eerst de verdeelde planningen per maand sommeren
            planningen = teamlid.planning_set.all()
            # teamlidipp_uren = {}
            # ipp_medewerk = {}
            teamleden[tl_naam]['ipp'] = {}
            for planning in planningen:

                ipp_soort = (planning.verdeeldeplanning_set
                                        .values('groep_maand')
                                        .annotate(uren_ipp = Sum('verdeling')))

                teamleden[tl_naam]['ipp'][planning.get_soort_display()] = {
                x['groep_maand']: x['uren_ipp'] for x in ipp_soort
                }

            # ipp uren en beschibare uren samenvoegen en bij het totaalniveau optellen
            teamleden[tl_naam]['beschikbaar'] = {}
            for u in uren_b:
                # Voor parttimers aantal beschikbare uren verminderen
                teamleden[tl_naam]['beschikbaar'][u['groep_maand']]  = u['beschikbaar'] * teamlid.fte

            # lijst van 12 maanden om waarden op te hangen
            kapstok = month_list(eind)


        results ={}
        # Alle teamleden langsgaan en dan wat 'housekeeping'
        for key in teamleden.keys():
            # print(str(key) + ' teamlid: ' + str(Employee.objects.get(pk = key)))
            # pp.pprint(teamleden[key])
            results[key] = {}
            # Afas uren
            results[key]['timecharts'] = [
            {'x':k, 'y': float(teamleden[key]['timecharts'].get(k, 0))} for k in kapstok
            ]
            # beschikbare uren
            results[key]['beschikbaar'] = [
            {'x': k, 'y': float(teamleden[key]['beschikbaar'].get(k, 0))} for k in kapstok
            ]
            # ipp uren
            results[key]['ipp'] ={}
            for key_b in teamleden[key]['ipp'].keys():
                # results[key]['ipp'] ={}
                results[key]['ipp'][key_b] = [
                {'x': k, 'y': float(teamleden[key]['ipp'][key_b].get(k, 0))} for k in kapstok
                ]

            results[key]['pk'] = teamleden[key]['pk']

        # pp.pprint(results)



        data_nvd = {'data_nieuw': results}



        return JsonResponse(data_nvd)


"""
Planning overzicht view. Geeft een lijst weer van
eerde gemaate planningen van een medewerker
"""
def planning_lijst(request, medewerker_id=None):

    # rol van de gebruiker uitpluizen
    emp = get_object_or_404(Employee, user = request.user)
    rol = get_role(emp)

    # Als om een specifieke medewerker wordt gevraagd deze proberen op te halen
    if medewerker_id:
        medewerker_id =  int(medewerker_id)
        medewerker = get_object_or_404(Employee, pk = int(medewerker_id))
        # heeft de gebruiker recht om deze client in te zien?
        # (gebruiker vraagt voor zichzelf of is teamleider en vraagt voor een van zijn team)
        if has_permission(test_id = medewerker_id, rol = rol, niveau = 'individueel'):
            planningen = medewerker.planning_set.all()
        # Geen rechten?, wegwezen
        else:
            messages.error(request, 'Geen rechten om de planningen van deze medewerker in te zien')
            return redirect(reverse('behandelaar'))

    # Als niet om een specifieke medewerker wordt gevraagd,
    # Dan proberen medewerker af te leiden uit user en te redirecten
    else:
        medewerker = get_object_or_404(Employee, user = request.user)
        return redirect('/planning/lijst/' + str(medewerker.pk) + '/')


    return render(request, 'productiviteit/planning_lijst.html',
                            {'rol': rol, 'planningen': planningen})




"""
View voor verschillende overzichten op vestigingsniveau
"""
def vestiging(request, vestiging_id=None):

        # medewerker uit user halen
        medewerker = get_object_or_404(Employee, user = request.user)

        # rol van gebruiker
        rol = get_role(medewerker)

        # lijst met jaren maken, huidig jaar en 2 jaar ervoor, maar niet lager dan 2016
        jaren = lijst_jaren

        # als er een specifieke vestiging wordt gevraagd. Dan krijgt je die als je
        # rechten hebt
        if vestiging_id:
            vestiging = get_object_or_404(Vestiging, pk = int(vestiging_id))


            # Check of deze gebruiker deze vestiging mag zien (teamleider)
            if has_permission(test_id = vestiging.pk, rol = rol, niveau = 'vestiging'):
                return render(request, 'productiviteit/home.html', {
                    'naam': vestiging, 'jaren': jaren, 'rol': rol, 'niveau': 'vestiging'})

            # Geen rechten?, wegwezen
            else:
                messages.error(request, 'Alleen de teamleider mag de vestigingspagina bekijken')
                return redirect(reverse('behandelaar'))


        # als er geen specifieke vestiging is gevraagd, kijken of we uit de user
        # een vestiging kunnen halen en daar naar redirecten
        else:
            return redirect('/vestiging/' + str(medewerker.vestiging.pk) + '/')


"""
View met overzicht behandelaars voor teamleider
"""

def behandelaar_lijst(request, vestiging_id=None):
        # medewerker uit user halen
        medewerker = get_object_or_404(Employee, user = request.user)

        # rol van gebruiker
        rol = get_role(medewerker)

        # als er een specifieke vestiging wordt gevraagd. Dan krijgt je die
        if vestiging_id:
            vestiging = get_object_or_404(Vestiging, pk = int(vestiging_id))
            # Check of deze gebruiker deze vestiging mag zien (teamleider)
            if has_permission(test_id = vestiging.pk, rol = rol, niveau = 'vestiging'):
                jaren = lijst_jaren
                return render(request, 'productiviteit/medewerker_lijst.html', {
                'naam': vestiging, 'niveau': 'vestiging', 'jaren': jaren})
