from django.forms import ModelForm
from django.forms import Textarea

from .models import Entrada
from .models import Diario


class CreateEntradaForm(ModelForm):
    class Meta:
        model = Entrada
        exclude = ['fecha_publicacion_entrada', 'fecha_edicion_entrada']
        widgets = {
            'texto_entrada': Textarea(attrs={'cols': 80, 'rows': 20}),
        }


class CreateDiarioForm(ModelForm):
    class Meta:
        model = Diario
        exclude = ['fecha_publicacion_entrada',
                   'fecha_edicion_entrada', 'visible_entrada']
        widgets = {
            'texto_entrada': Textarea(attrs={'cols': 80, 'rows': 20}),
        }
