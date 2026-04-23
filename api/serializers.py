from rest_framework import serializers
from .models import Actividad, Subtarea, UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Sum
from decimal import Decimal

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

        # Validar campos obligatorios solo en creación (POST)
        if not self.partial:
            if not data.get("nombre"):
                errores["nombre"] = "El nombre es obligatorio."

            horas = data.get("horas_estimadas")

            if horas is None or horas <= 0:
                errores["horas_estimadas"] = "Las horas estimadas deben ser mayores a 0."

            if not data.get("fecha_entrega"):
                errores["fecha_entrega"] = "La fecha de entrega es obligatoria."

        # Validar límite diario (tanto en creación como en actualización)
        # Si es PATCH, usar valores del instance si no se proporcionan
        horas = data.get("horas_estimadas")
        fecha_entrega = data.get("fecha_entrega")
        
        if self.instance and self.partial:
            # En PATCH, usar valores existentes si no se proporcionan
            if horas is None:
                horas = self.instance.horas_estimadas
            if fecha_entrega is None:
                fecha_entrega = self.instance.fecha_entrega
        
        # Obtener actividad (en PATCH viene de instance)
        actividad = data.get("actividad")
        if self.instance and not actividad:
            actividad = self.instance.actividad
        
        if actividad and fecha_entrega and horas:
            usuario = actividad.usuario
            try:
                limite = usuario.profile.limite_diario_horas
            except:
                limite = Decimal('6.00')
            
            # Calcular total de horas en esa fecha (excluyendo esta subtarea si es actualización)
            otras_subtareas = Subtarea.objects.filter(
                actividad__usuario=usuario,
                fecha_entrega=fecha_entrega
            )
            
            if self.instance:
                otras_subtareas = otras_subtareas.exclude(id=self.instance.id)
            
            total_otras_horas = otras_subtareas.aggregate(
                total=Sum('horas_estimadas')
            )['total'] or Decimal('0')
            
            total_horas = total_otras_horas + Decimal(str(horas))
            
            if total_horas > limite:
                errores["horas_estimadas"] = (
                    f"Las horas totales para {fecha_entrega} "
                    f"({total_horas}h) excederían el límite diario de {limite}h. "
                    f"Otras tareas ese día: {total_otras_horas}h"
                )
        
        # Validar que horas_estimadas sea mayor a 0
        if horas is not None and horas <= 0:
            errores["horas_estimadas"] = "Las horas estimadas deben ser mayores a 0."

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

        # Validar límite diario si se proporciona una fecha y horas estimadas
        if data.get("fecha") and data.get("horas_est"):
            usuario = self.context.get('request').user if self.context.get('request') else None
            
            if usuario:
                try:
                    limite = usuario.profile.limite_diario_horas
                except:
                    limite = Decimal('6.00')
                
                fecha = data.get("fecha")
                horas = Decimal(str(data.get("horas_est")))
                
                # Calcular total de horas en esa fecha (excluyendo esta actividad si es actualización)
                otras_actividades = Actividad.objects.filter(
                    usuario=usuario,
                    fecha=fecha
                )
                
                # Incluir también subtareas de otras actividades
                otras_subtareas = Subtarea.objects.filter(
                    actividad__usuario=usuario,
                    fecha_entrega=fecha
                )
                
                if self.instance:
                    otras_actividades = otras_actividades.exclude(id=self.instance.id)
                
                total_otras_actividades = otras_actividades.aggregate(
                    total=Sum('horas_est')
                )['total'] or Decimal('0')
                
                total_subtareas = otras_subtareas.aggregate(
                    total=Sum('horas_estimadas')
                )['total'] or Decimal('0')
                
                total_horas = horas + total_otras_actividades + total_subtareas
                
                if total_horas > limite:
                    errores["horas_est"] = (
                        f"Las horas totales para {fecha} "
                        f"({total_horas}h) excederían el límite diario de {limite}h. "
                        f"Otras actividades: {total_otras_actividades}h, "
                        f"Subtareas: {total_subtareas}h"
                    )

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
        
        # Crear automáticamente el UserProfile
        UserProfile.objects.get_or_create(usuario=user)
        
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


# =========================
# Usuario Profile - Límite Diario
# =========================
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'usuario', 'limite_diario_horas', 'created_at', 'updated_at']
        read_only_fields = ['id', 'usuario', 'created_at', 'updated_at']

    def validate_limite_diario_horas(self, value):
        if value < 1:
            raise serializers.ValidationError("El límite diario debe ser al menos 1 hora.")
        if value > 16:
            raise serializers.ValidationError("El límite diario no puede exceder 16 horas.")
        return value