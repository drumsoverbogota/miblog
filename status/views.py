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


    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        latest = Status.objects.latest('fecha')
        serializer = StatusSerializer(latest) 
        return Response(serializer.data, status=status.HTTP_200_OK)    


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
        latest = Status.objects.latest('fecha')
        serializer = StatusSerializer(latest) 
        date_str = serializer.data["fecha"]
        status = serializer.data["status"]
        date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
        present = datetime.now(timezone.utc) - date_obj

        diferencia = present.seconds
        if status == "OFF":
            context["status"] = "El servidor está apagado"
            context["imagen"] = "apagado"
        elif diferencia > TIEMPO_MAX:
            context["status"] = f"No hay comunicacion hace más de {MINUTOS} minutos, es posible que no haya Internet o esté apagado"
            context["imagen"] = f"norespuesta"
        else:
            context["status"] = f"El servidor está funcionando!"
            context["imagen"] = f"internet"
        
        return context
    
def redirect_view(request):
    latest = Status.objects.latest('fecha')
    serializer = StatusSerializer(latest)
    ip = serializer.data["ip"]
    print(ip)
    return redirect(f'http://{ip}')