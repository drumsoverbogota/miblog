from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from blog import settings

from . import views

app_name = 'entradas'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('twitter/<slug:slug>', views.TwitterView.as_view(), name='twitter'),
    path('diario', views.DiarioIndexView.as_view(), name='diarioindex'),
    path('diario/create', views.CreateDiarioView.as_view(), name='diariocreate'),
    path('diario/<slug:slug>', views.DetailDiarioView.as_view(), name='diariodetail'),    
    path('diario/delete/<slug:slug>', views.DeleteDiarioView.as_view(), name='diariodelete'),
    path('diario/edit/<slug:slug>', views.EditDiarioView.as_view(), name='diarioedit'),
    path('diario/tags/<slug:tag>', views.DiarioTagView.as_view(), name='diariotags'),
    path('tags/<slug:tag>', views.TagView.as_view(), name='tags'),
    path('entradas/create', views.CreateEntradaView.as_view(), name='create'),
    path('entradas/<slug:slug>', views.DetailEntradaView.as_view(), name='detail'),    
    path('entradas/delete/<slug:slug>', views.DeleteEntradaView.as_view(), name='delete'),
    path('entradas/edit/<slug:slug>', views.EditEntradaView.as_view(), name='edit'),
    path('imagenes', views.SubirImagenView.as_view(), name='imagen'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)