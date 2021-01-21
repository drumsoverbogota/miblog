from django.contrib import admin

from .models import Entrada
from .models import Diario

admin.site.register(Entrada)
admin.site.register(Diario)
