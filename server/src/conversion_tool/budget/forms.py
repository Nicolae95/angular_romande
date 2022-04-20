from .models import *
from django import forms
from django.utils.translation import ugettext_lazy as _


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ('pfc', 'pfc_market', 'cc' )

    def __init__(self, *args, **kwargs):
        super(BudgetForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # field.widget.attrs['required'] = 'required'
            field.widget.attrs['class'] = 'form-control'
            self.fields['pfc_market'].required = False
            self.fields['pfc'].required = False
