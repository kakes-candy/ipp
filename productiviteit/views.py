from django.contrib.auth.views import login
from django.contrib import messages
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from .models import Planning, Employee, Dagen, Feestdagen, VerdeeldePlanning, Timechart, Vestiging
from .forms import PlanningForm
from django.contrib.auth.models import User
from django.forms import formset_factory, modelformset_factory
from django.db import IntegrityError, transaction
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count, Value
from django.core.urlresolvers import reverse
from django.http import JsonResponse
import datetime, time
from django.db.models import Prefetch


# Home View.
def home(request, **kwargs):
    if request.user.is_authenticated():
        medewerker = Employee.objects.get(user = request.user)
        rol = {}
        if Vestiging.objects.filter(teamleider = medewerker).exists():
            rol['naam'] = 'teamleider'
        else:
            rol['naam'] = 'behandelaar'

        # lijst met jaren maken, huidig jaar en 2 jaar ervoor, maar niet lager dan 2016
        # het zou mooier zijn om te kijken welke jaren in de data zitten, maar dat kost teveel tijd
        jaren = []
        # 1 januari van dit jaar opslaan
        vandaag = datetime.datetime.today().date().replace(month=1).replace(day=1)
        for i in range(0, 3):
            date = vandaag.replace(year=(vandaag.year-i))
            if date.year >= 2016:
                jaren.append(date)

        return render(request, 'productiviteit/home.html', {'naam': medewerker, 'jaren': jaren, 'rol': rol})
    else:
        return login(request)

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
    else:
        edit = False
        extra = 1
        qset = Planning.objects.none()

    planning_formset = modelformset_factory(Planning, form = PlanningForm, extra = extra)
    formset = planning_formset(queryset = qset)

    if request.method == 'POST':
        formset = planning_formset(request.POST)
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

            return redirect(reverse('home'))


    return render(request, 'productiviteit/planning_create.html', {'planning_formset': formset, 'edit': edit})

    #     planning_formset = PlanningFormSet(request.POST)
    #
    #     if planning_formset.is_valid():
    #         verdelingen_to_save = []
    #
    #         for planning in planning_formset:
    #             soort = planning.cleaned_data.get('soort')
    #             startdatum = planning.cleaned_data.get('startdatum')
    #             einddatum = planning.cleaned_data.get('einddatum')
    #             hoeveelheid = planning.cleaned_data.get('hoeveelheid')
    #
    #             if soort and startdatum and einddatum and hoeveelheid:
    #
    #
    #                 # werkdagen ophalen in de opgegegen periode
    #                 werkdagen = Dagen.objects.filter(dag__gte=startdatum, dag__lte=einddatum,
    #                 dag__week_day__in=[2,3,4,5,6]).exclude(feestdagen__vrije_dag__isnull = False)
    #
    #                 if len(werkdagen) == 0:
    #                     print('geen werkdagen')
    #                     messages.error(request, "Er zijn geen werkdagen gevonden tussen " + str(startdatum) + " en " + str(einddatum))
    #                     return render(request, 'productiviteit/planning_create.html', {'planning_formset': planning_formset})
    #                 else:
    #                     # Planningsobject maken
    #                     planning_to_save = Planning.objects.create(medewerker = medewerker,
    #                         soort = soort, startdatum = startdatum, einddatum = einddatum,
    #                         hoeveelheid = hoeveelheid)
    #
    #                     verdeelde_hoeveelheid = hoeveelheid / werkdagen.count()
    #
    #                     for item in werkdagen:
    #                         werkdag = item.dag
    #                         verdelingen_to_save.append(VerdeeldePlanning(planning = planning_to_save,
    #                             datum = item.dag, verdeling = verdeelde_hoeveelheid))
    #
    #                     VerdeeldePlanning.objects.bulk_create(verdelingen_to_save)
    #
    #     else:
    #         return render(request, 'productiviteit/planning_create.html', {'planning_formset': planning_formset})
    #
    #     return redirect(reverse('home'))
    #
    # else:
    #     return render(request, 'productiviteit/planning_create.html', {'planning_formset': PlanningFormSet})
    #

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



    if request.method == 'POST':
        if request.is_ajax():
            user = request.user
            medewerker = Employee.objects.get(user = user)
            naam = medewerker
            niveau = request.POST.get('niveau', 'i')
            if niveau == 'v':
                vestiging = medewerker.vestiging
                med_lijst = vestiging.employee_set.values_list('pk')
            elif niveau == 'i':
                med_lijst = [medewerker.pk]

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

            # regels voor prefetch van afas uren
            p_afas = Prefetch('pnummer',
                queryset = Timechart.objects.filter(datum__gte=start, datum__lte=eind, direct='1.0')\
                            .annotate(groep_maand = TruncMonth('datum')))

            # regels voor prefetch ipp uren
            p_ipp = Prefetch('planning_set__verdeeldeplanning_set',
                queryset = VerdeeldePlanning.objects.filter(datum__gte=start, datum__lte=eind) \
                            .annotate(groep_maand = TruncMonth('datum')))

            # gegevens ophalen van medewerkers, aangevuld met afas en ipp uren
            totaal = Employee.objects.filter(pk__in = med_lijst).prefetch_related(p_afas, p_ipp)


            # afas en ipp prefetches verder verwerken
            totaal_afas = {}
            totaal_beschikbaar = {}

            for t in totaal:
                #  Afas uren per maand uitrekenen en daarna optellen bij een totaaltelling
                afas = t.pnummer.values('groep_maand').annotate(uren_direct = Sum('aantal'))
                for a in afas:
                    old_a = totaal_afas.get(a['groep_maand'], 0)
                    totaal_afas[a['groep_maand']] = old_a + a['uren_direct']

                # Ipp planningen hebben 2 niveaus, de planning en de verdeelde planning, die meerdere
                # maanden kan bevatten. Eerst de verdeelde planningen per maand sommeren
                planning = t.planning_set.all()
                ipp_medewerk = {}
                for p in planning:
                    ipp_by_month = p.verdeeldeplanning_set.values('groep_maand').annotate(uren_ipp = Sum('verdeling'))
                    for month in ipp_by_month:
                        old = ipp_medewerk.get(month['groep_maand'], 0)
                        ipp_medewerk[month['groep_maand']] = old + month['uren_ipp']

                # ipp uren en beschibare uren samenvoegen en bij het totaalniveau optellen
                for u in uren_b:
                    beschikbaar_tot = totaal_beschikbaar.get(u['groep_maand'], 0)
                    ipp_med_mnd = float(ipp_medewerk.get(u['groep_maand'], 0))
                    beschikbaar_mnd = u['beschikbaar'] * t.fte
                    netto = beschikbaar_mnd - ipp_med_mnd
                    totaal_beschikbaar[u['groep_maand']] = beschikbaar_tot + netto

            # lijst van 12 maanden om waarden op te hangen
            kapstok = month_list(eind)

            # Beschikbare uren berekenen op basis van werk en feestdagen * fte,
            # dan ipp uren daarvan af halen. In formaat zetten dat door nvd3 verwacht wordt
            beschikbaar_netto = []
            beschikbaar_netto_cum = []
            cum_b = 0
            for k in kapstok:
                kc = time.mktime(k.timetuple()) * 1000
                netto = totaal_beschikbaar.get(k, 0)
                cum_b = cum_b + netto
                beschikbaar_netto.append({'y': int(netto), 'x': k})
                beschikbaar_netto_cum.append({'y': int(cum_b), 'x': kc})


            # Hetzelfde doen voor de uren afkomstig uit WeCare/AFAS
            direct = []
            direct_cum = []
            cum_d = 0
            for k in kapstok:
                kc = time.mktime(k.timetuple()) * 1000
                d = round(totaal_afas.get(k, 0))
                cum_d = cum_d + d
                direct.append({'y': d, 'x': k})
                direct_cum.append({'y': cum_d, 'x': kc})

            data_nvd = {'data' : [ {'key': 'beschikbaar', 'color': '#5F9EA0', 'values': beschikbaar_netto},
            {'key': 'gerealiseerd', 'color': '#FF7F50', 'values': direct}],
            'cumulatief':  [ {'key': 'beschikbaar', 'color': '#5F9EA0', 'values': beschikbaar_netto_cum},
            {'key': 'gerealiseerd', 'color': '#FF7F50', 'values': direct_cum}]}

            return JsonResponse(data_nvd)
