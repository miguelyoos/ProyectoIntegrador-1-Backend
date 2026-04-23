from rest_framework.response import Response
from django.utils import timezone
from rest_framework import viewsets, status
from .models import Actividad, Subtarea, UserProfile
from .serializers import (
    ActividadSerializer,
    SubtareaSerializer,
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

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

class VistaHoyView(APIView):
    permission_classes = [IsAuthenticated]

    REGLA = [
        "1. Vencidas primero: la subtarea con fecha más antigua aparece arriba.",
        "2. Luego las de hoy, ordenadas por menor esfuerzo estimado.",
        "3. Luego Próximas, por fecha más cercana primero.",
        "4. Empate en fecha: se desempata por menor esfuerzo estimado.",
    ]

    def get(self, request):
        hoy = timezone.now().date()

        materia = request.query_params.get('materia')
        estado  = request.query_params.get('estado')

        base_query = Subtarea.objects.filter(
            actividad__usuario=request.user
        ).select_related('actividad')

        if materia:
            base_query = base_query.filter(actividad__materia__iexact=materia)
        if estado:
            base_query = base_query.filter(actividad__estado=estado)

        vencidas = base_query.filter(
            fecha_entrega__lt=hoy
        ).order_by('fecha_entrega', 'horas_estimadas')

        para_hoy = base_query.filter(
            fecha_entrega=hoy
        ).order_by('horas_estimadas')

        proximas = base_query.filter(
            fecha_entrega__gt=hoy
        ).order_by('fecha_entrega', 'horas_estimadas')

        if not vencidas.exists() and not para_hoy.exists() and not proximas.exists():
            return Response({
                "vacia": True,
                "mensaje": "No tienes subtareas para mostrar.",
                "accion": "Crear actividad",
                "regla": self.REGLA,
                "vencidas": [],
                "para_hoy": [],
                "proximas": [],
            })

        return Response({
            "vacia": False,
            "regla": self.REGLA,
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


class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "username": getattr(user, 'username', ''),
                    "first_name": getattr(user, 'first_name', ''),
                    "last_name": getattr(user, 'last_name', ''),
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )




class EmailLoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Obtener el perfil del usuario actual con su límite diario"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(usuario=request.user)
        
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Actualizar el límite diario del usuario"""
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(usuario=request.user)
        
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "detail": "Límite diario actualizado correctamente",
                    "profile": serializer.data
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)