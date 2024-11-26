from django.views.generic.base import TemplateView
from django.shortcuts import redirect
from rest_framework.views import APIView
from .serializers import StatusSerializer
from .models import Status
from datetime import datetime, timezone
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.decorators import api_view, permission_classes
# Create your views here.

MINUTOS = 15
TIEMPO_MAX = 60 * MINUTOS

class StatusAPIView(APIView):

    queryset = Status.objects.all()
    permission_classes = [DjangoModelPermissions]

    def post(self, request, format=None):
        """
        Return a list of all users.
        """
        serializer = StatusSerializer(data=request.data) 
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, 
                            status=status.HTTP_201_CREATED) 
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StatusView(TemplateView):
    template_name = 'status/status.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if len(Status.objects.all()) > 0:
            latest = Status.objects.latest('fecha')
            if latest:
                date_obj = latest.fecha
                ip = latest.ip
                present = datetime.now(timezone.utc) - date_obj

                diferencia = present.seconds
                if latest.status == "OFF":
                    context["status"] = "El servidor está apagado."
                    context["imagen"] = "apagado"
                    print("B")
                elif diferencia > TIEMPO_MAX:
                    context["status"] = f"No hay comunicacion hace más de {MINUTOS} minutos, es posible que no haya Internet o esté apagado"
                    context["direccion"] = f"La última dirección disponible fue: {ip}"
                    context["imagen"] = f"norespuesta"
                else:
                    context["status"] = f"El servidor está funcionando!"
                    context["direccion"] = f"La dirección es: http://{ip}"
                    context["imagen"] = f"internet"
        else: 
            context["status"] = f"No hay registro :B"
            context["imagen"] = f"internet"            
        return context
    