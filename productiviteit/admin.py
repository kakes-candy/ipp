from django.contrib import admin
from .models import Employee, Timechart, Vestiging, Regio, Planning, Functie, Dagen, Feestdagen, VerdeeldePlanning

# medewerkers, vestigingen en regios tabellen in admin
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('voornaam', 'tussenvoegsels', 'achternaam', 'vestiging', 'functie')
    search_fields =('voornaam', 'achternaam')

admin.site.register(Employee, EmployeeAdmin)

class PlanningAdmin(admin.ModelAdmin):
    list_display = ('medewerker', 'soort', 'startdatum', 'einddatum', 'hoeveelheid')

admin.site.register(Planning, PlanningAdmin)

class VerdeeldePlanningAdmin(admin.ModelAdmin):
    list_display = ('planning', 'datum', 'verdeling')

admin.site.register(VerdeeldePlanning, VerdeeldePlanningAdmin)

class VestigingAdmin(admin.ModelAdmin):
    list_display = ('naam', 'teamleider', 'bij_regio')

admin.site.register(Vestiging, VestigingAdmin)


admin.site.register(Regio)

admin.site.register(Functie)
# en de tijden activeren in admin
admin.site.register(Timechart)



class FeestdagenAdmin(admin.ModelAdmin):
    list_display = ('dag', 'vrije_dag')
    ordering = ('dag',)

admin.site.register(Feestdagen, FeestdagenAdmin)



# # Zinloze tabel om te bekijken
# class DagenAdmin(admin.ModelAdmin):
#     ordering = ('dag',)
#
# admin.site.register(Dagen, DagenAdmin)
