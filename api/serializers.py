from rest_framework import serializers
from .models import Actividad, Subtarea
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']
        read_only_fields = ['id']

    def validate_email(self, value):
        normalized = value.strip().lower()
        if User.objects.filter(email__iexact=normalized).exists():
            raise serializers.ValidationError('Ya existe un usuario con este email.')
        return normalized

    def create(self, validated_data):
        password = validated_data.pop('password')
        username = validated_data.get('username', '').strip()
        email = validated_data.get('email', '').strip().lower()

        if not username:
            base_username = email.split('@')[0] if '@' in email else email
            candidate = base_username
            suffix = 1
            while User.objects.filter(username=candidate).exists():
                candidate = f"{base_username}{suffix}"
                suffix += 1
            validated_data['username'] = candidate

        user = User.objects.create_user(password=password, **validated_data)
        return user


class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user_by_email = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Credenciales incorrectas")

        user = authenticate(
            request=self.context.get('request'),
            username=getattr(user_by_email, User.USERNAME_FIELD),
            password=password,
        )

        if not user:
            raise serializers.ValidationError("Credenciales incorrectas")

        refresh = RefreshToken.for_user(user)

        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": getattr(user, 'username', ''),
                "first_name": getattr(user, 'first_name', ''),
                "last_name": getattr(user, 'last_name', ''),
            },
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }