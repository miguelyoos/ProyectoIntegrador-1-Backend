from rest_framework import serializers
from .models import Actividad, Subtarea
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
User = get_user_model()


# =========================
# US-02 — Crear Subtarea
# =========================
class SubtareaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subtarea
        fields = '__all__'

    def validate(self, data):
        errores = {}

        # SOLO validar en creación o PUT
        if not self.partial:

            if not data.get("nombre"):
                errores["nombre"] = "El nombre es obligatorio."

            horas = data.get("horas_estimadas")

            if horas is None or horas <= 0:
                errores["horas_estimadas"] = "Las horas estimadas deben ser mayores a 0."

            if not data.get("fecha_entrega"):
                errores["fecha_entrega"] = "La fecha de entrega es obligatoria."

        if errores:
            raise serializers.ValidationError(errores)

        return data


# =========================
# US-01 — Crear Actividad
# =========================
class ActividadSerializer(serializers.ModelSerializer):
    subtareas = SubtareaSerializer(many=True, read_only=True)
    horas_est = serializers.FloatField(required=False)
    horas_comp = serializers.FloatField(required=False)

    class Meta:
        model = Actividad
        fields = '__all__'
        read_only_fields = ['usuario']

    def to_internal_value(self, data):
        # Convertir camelCase a snake_case para compatibilidad con frontend
        if 'horasEst' in data:
            data['horas_est'] = data.pop('horasEst')
        if 'horasComp' in data:
            data['horas_comp'] = data.pop('horasComp')
        
        # Normalizar valores de estado para compatibilidad con frontend
        if 'estado' in data:
            estado_map = {
                'progreso': 'en_progreso',
                'en progreso': 'en_progreso',
                'completado': 'completada',
            }
            data['estado'] = estado_map.get(data['estado'], data['estado'])
        
        return super().to_internal_value(data)
    
    def to_representation(self, instance):
        # Convertir snake_case a camelCase en la respuesta
        data = super().to_representation(instance)
        data['horasEst'] = data.pop('horas_est')
        data['horasComp'] = data.pop('horas_comp')
        return data

    def validate(self, data):
        errores = {}

        # Solo validar campos obligatorios si no es una actualización parcial
        if not self.partial:
            if not data.get("titulo"):
                errores["titulo"] = "El título es obligatorio."

            if not data.get("tipo"):
                errores["tipo"] = "El tipo es obligatorio."

            if not data.get("materia"):
                errores["materia"] = "La materia es obligatoria."

        if errores:
            raise serializers.ValidationError(errores)

        return data
class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Credenciales incorrectas")

        if not user.check_password(password):
            raise serializers.ValidationError("Credenciales incorrectas")

        refresh = RefreshToken.for_user(user)

        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }