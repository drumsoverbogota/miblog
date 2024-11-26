from django.urls import path

from . import views

app_name = 'urls'

urlpatterns = [
    path('statusapi/', views.StatusAPIView.as_view()),
    path('status/', views.StatusView.as_view()),
    path('servidor/', views.redirect_view),
]
