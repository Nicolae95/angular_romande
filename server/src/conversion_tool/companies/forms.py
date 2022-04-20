from companies.models import Company, Meter, Site
from django import forms

class MeterForm(forms.ModelForm):
    class Meta:
        model = Meter
        fields = ('meter_id', 'site')

    def __init__(self, *args, **kwargs):
        super(MeterForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'site':
                field.widget.attrs['class'] = 'selectpicker form-control'
                field.widget.attrs['data-live-search'] = 'true'
            else :
                field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = 'required'

class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ('name', 'location', 'company')

    def __init__(self, *args, **kwargs):
        super(SiteForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in ['location', 'company']:
                field.widget.attrs['class'] = 'selectpicker form-control'
                field.widget.attrs['data-live-search'] = 'true'
            else :
                field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = 'required'

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['required'] = 'required'
