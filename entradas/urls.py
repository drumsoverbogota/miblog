from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.urls import path

from blog import settings

from . import views

app_name = 'entradas'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('diario', views.DiarioIndexView.as_view(), name='diarioindex'),
    path('diario/<int:pk>', views.DetailDiarioView.as_view(), name='diariodetail'),
    path('diario/create', views.CreateDiarioView.as_view(), name='diariocreate'),
    path('diario/delete/<int:pk>', views.DeleteDiarioView.as_view(), name='diariodelete'),
    path('diario/edit/<int:pk>', views.EditDiarioView.as_view(), name='diarioedit'),
    path('diario/tags/<slug:tag>', views.DiarioTagView.as_view(), name='diariotags'),
    path('tags/<slug:tag>', views.TagView.as_view(), name='tags'),
    path('entradas/<int:pk>', views.DetailEntradaView.as_view(), name='detail'),
    path('entradas/create', views.CreateEntradaView.as_view(), name='create'),
    path('entradas/delete/<int:pk>', views.DeleteEntradaView.as_view(), name='delete'),
    path('entradas/edit/<int:pk>', views.EditEntradaView.as_view(), name='edit'),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)