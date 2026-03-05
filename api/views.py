from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import F
from .models import Subtarea
from .serializers import SubtareaSerializer
from django.shortcuts import render
from rest_framework import viewsets
from .models import Actividad, Subtarea
from .serializers import ActividadSerializer, SubtareaSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailTokenObtainPairSerializer

class ActividadViewSet(viewsets.ModelViewSet):
    queryset = Actividad.objects.all()
    serializer_class = ActividadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Optimización: cargar subtareas en una sola consulta
        return self.queryset.filter(usuario=self.request.user).prefetch_related('subtareas')
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
class SubtareaViewSet(viewsets.ModelViewSet):
    queryset = Subtarea.objects.all()
    serializer_class = SubtareaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Optimización: filtrar por usuario y cargar actividad en una consulta
        return self.queryset.filter(actividad__usuario=self.request.user).select_related('actividad')

@api_view(['GET'])
def vista_hoy(request):
    hoy = timezone.now().date()
    
    # Optimización: filtrar por usuario y cargar actividad en una consulta
    base_query = Subtarea.objects.filter(
        actividad__usuario=request.user
    ).select_related('actividad')

    vencidas = base_query.filter(
        fecha_entrega__lt=hoy
    ).order_by('fecha_entrega', 'horas_estimadas')

    para_hoy = base_query.filter(
        fecha_entrega=hoy
    ).order_by('horas_estimadas')

    proximas = base_query.filter(
        fecha_entrega__gt=hoy
    ).order_by('fecha_entrega', 'horas_estimadas')

    return Response({
        "regla": "Vencidas primero (más antiguas arriba), luego Para hoy, luego Próximas por fecha más cercana. Empate: menor esfuerzo primero.",
        "vencidas": SubtareaSerializer(vencidas, many=True).data,
        "para_hoy": SubtareaSerializer(para_hoy, many=True).data,
        "proximas": SubtareaSerializer(proximas, many=True).data,
    })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() 

            return Response(
                {"detail": "Sesión cerrada correctamente"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {"error": "Token inválido"},
                status=status.HTTP_400_BAD_REQUEST
            )




class EmailLoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer