from django.forms import ModelForm
from core.models import Consulta
from bootstrap_datepicker_plus import DatePickerInput

class QueryForm(ModelForm):
    class Meta:
        model = Consulta
        fields = ['peticion', 'fecha_inicial','fecha_final']
        widgets = {
            'fecha_inicial': DatePickerInput(format="%d/%m/%Y"),
            'fecha_final': DatePickerInput(format="%d/%m/%Y"),
        }

