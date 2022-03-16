from django.db import models
from django.utils import timezone

from taggit.managers import TaggableManager


class Base(models.Model):
    titulo_entrada = models.CharField(max_length=200, blank=True)
    slug = models.CharField(max_length=200, blank=False, unique=True, default='empty')
    fecha_publicacion_entrada = models.DateTimeField(
        'Fecha publicado', default=timezone.now)
    fecha_edicion_entrada = models.DateTimeField(
        'Fecha editado', blank=True, null=True, default=timezone.now)
    imagen_entrada = models.FileField(blank=True, null=True, upload_to='imagenes/')
    texto_entrada = models.TextField(blank=True, null=True)
    tags_entrada = TaggableManager(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        if self.fecha_publicacion_entrada:
            return '%s (%s-%s-%s)' % (self.titulo_entrada, self.fecha_publicacion_entrada.day,
                                      self.fecha_publicacion_entrada.month, self.fecha_publicacion_entrada.year)
        else:
            return self.titulo_entrada


class Entrada(Base):
    visible_entrada = models.BooleanField(default=True)


class Diario(Base):
    pass


class Comentario(models.Model):
    entrada = models.ForeignKey(Entrada, on_delete=models.CASCADE)
    autor_comentario = models.CharField(max_length=255)
    correo_autor_comentario = models.CharField(max_length=200)
    fecha_publicacion_comentario = models.DateTimeField('Fecha publicado')
    texto_comentario = models.TextField()
    visible_comentario = models.BooleanField()


class Imagen(models.Model):
    imagen = models.FileField(blank=True, null=True, upload_to='imagenes/')
    nombre_imagen = models.CharField(max_length=200, blank=False)
    fecha_publicacion_imagen = models.DateTimeField(
        'Fecha agregada', default=timezone.now)    