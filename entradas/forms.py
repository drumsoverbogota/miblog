from django.forms import Form
from django.forms import ModelChoiceField
from django.forms import CharField
from django.forms import ModelForm
from django.forms import Textarea

from .models import Entrada
from .models import Diario

class TwitterForm(Form):
    tweet = CharField(max_length=280)


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
