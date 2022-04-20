from .models import *
from django import forms
from geo.models import Location, Holiday
from django.utils.translation import ugettext_lazy as _

class EnergyConsumptionFileForm(forms.ModelForm):
    class Meta:
        model = EnergyConsumptionFile
        fields = ('data_file', 'site')

    def __init__(self, *args, **kwargs):
        super(EnergyConsumptionFileForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'site':
                field.widget.attrs['class'] = 'selectpicker form-control'
                field.widget.attrs['data-live-search'] = 'true'
                field.widget.attrs['data-size'] = '10'
            else :
                field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = 'required'

class EnergyConsumptionReportForm(forms.ModelForm):
    class Meta:
        model = EnergyConsumptionReport
        fields = ('title', 'meter', 'shedules', 'datetime_from', 'datetime_to', 'time_peak', 'time_peakoff', 'unit')

    def __init__(self, *args, **kwargs):
        super(EnergyConsumptionReportForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['meter', 'shedules', 'unit']:
                field.widget.attrs['class'] = 'selectpicker form-control'
                # field.widget.attrs['data-max-options'] = '2'
                field.widget.attrs['data-actions-box'] = 'true'
                field.widget.attrs['data-live-search'] = 'true'
                field.widget.attrs['data-size'] = '10'
            else :
                field.widget.attrs['class'] = 'form-control'
