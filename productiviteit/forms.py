from django import forms
from .models import Planning
from django.forms import BaseModelFormSet
from django.forms import formset_factory


class PlanningForm(forms.ModelForm):



    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        # print("uit de form init: " + str(gebruiker.username))
        super(PlanningForm, self).__init__(*args, **kwargs)
        keuzes = self.fields['soort'].choices
        def choicefilter(choices, excluded):
            return [item for item in choices if item[0] not in excluded]
        if self.user.username == 'mschrijver':
            self.fields['soort'].choices = choicefilter(choices = keuzes, excluded = ['MLV', 'KP', 'OLD', 'WO', 'WBG_K'])


    def clean(self):
        cleaned_data = super(PlanningForm, self).clean()
        startdatum = cleaned_data.get("startdatum")
        einddatum = cleaned_data.get("einddatum")

        if startdatum and einddatum:
            # Only do something if both fields are valid so far.
            if startdatum > einddatum:
                raise forms.ValidationError(
                    "De einddatum mag niet voor de startdatum zijn"
                )
    def clean_hoeveelheid(self):
        hoeveelheid = self.cleaned_data['hoeveelheid']
        print(str(type(hoeveelheid)))
        if not hoeveelheid or hoeveelheid <= 0.0:
            raise forms.ValidationError(
                "Je hebt geen hoeveelheid ingevuld"
            )
        return(hoeveelheid)


    class Meta:
        model = Planning
        fields = ('soort', 'startdatum', 'einddatum', 'hoeveelheid',)
        labels = {'hoeveelheid' : 'Uren'}
        widgets = {
        'soort': forms.Select(attrs={"class": "form-control"}),
        'startdatum': forms.DateInput(attrs={'class': 'datetimepicker form-control'}),
        'einddatum': forms.DateInput(attrs={'class': 'datetimepicker form-control'}),
        'hoeveelheid': forms.NumberInput(attrs = {'class': 'form-control', 'step': '0.25'})
        }
