from django.db import models
from django.utils import timezone

ENCENDIDO = 'ON'
APAGADO = 'OFF'
CHOICES = [
    (ENCENDIDO, 'Encendido'),
    (APAGADO, 'Apagado'),
]

# Create your models here.
class Status(models.Model):
    status = models.CharField(
        max_length=3,
        choices=CHOICES
    )
    ip = models.CharField(max_length=255)
    fecha = models.DateTimeField(
        'Fecha agregada', default=timezone.now)
