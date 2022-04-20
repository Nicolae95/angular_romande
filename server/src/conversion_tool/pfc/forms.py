from .models import *
from django import forms
from geo.models import Location, Holiday
from django.utils.translation import ugettext_lazy as _

class PfcConsumptionFileForm(forms.ModelForm):
    class Meta:
        model = PfcConsumptionFile
        fields = ('data_file', )

    def __init__(self, *args, **kwargs):
        super(PfcConsumptionFileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = 'required'
