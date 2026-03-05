from rest_framework import serializers
from .models import Actividad, Subtarea
from django.contrib.auth import authenticate
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
User = get_user_model()

# =========================
# US-01 — Crear Actividad
# =========================
class ActividadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Actividad
        fields = '__all__'

    def validate(self, data):
        errores = {}

        if not data.get("titulo"):
            errores["titulo"] = "El título es obligatorio."

        if not data.get("tipo"):
            errores["tipo"] = "El tipo es obligatorio."

        if not data.get("materia"):
            errores["materia"] = "La materia es obligatoria."

        if errores:
            raise serializers.ValidationError(errores)

        return data


# =========================
# US-02 — Crear Subtarea
# =========================
class SubtareaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subtarea
        fields = '__all__'

    def validate(self, data):
        errores = {}

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
class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Credenciales incorrectas")

        if not user.check_password(password):
            raise serializers.ValidationError("Credenciales incorrectas")

        # Aquí usamos el username REAL que ya existe en tu BD
        data = super().validate({
            "username": user.username,
            "password": password
        })

        return data