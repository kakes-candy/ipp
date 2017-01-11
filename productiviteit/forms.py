from django import forms
from .models import Planning


class PlanningForm(forms.ModelForm):

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
        'soort': forms.Select(attrs={"class": "formveld"}),
        'startdatum': forms.DateInput(attrs={'class': 'datetimepicker formveld'}),
        'einddatum': forms.DateInput(attrs={'class': 'datetimepicker formveld'}),
        'hoeveelheid': forms.NumberInput(attrs = {'class': 'formveld', 'step': '0.25'})
        }
