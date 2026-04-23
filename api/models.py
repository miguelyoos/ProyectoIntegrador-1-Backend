from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator



class Actividad(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='actividades'
    )

    TIPO_CHOICES = [
        ('Tarea', 'Tarea'),
        ('Examen', 'Examen'),
        ('Taller', 'Taller'),
        ('Proyecto', 'Proyecto'),
        ('Quiz', 'Quiz'),
    ]

    PRIORIDAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
        ('Urgente', 'Urgente'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En progreso'),
        ('completada', 'Completada'),
    ]

    titulo         = models.CharField(max_length=255)
    tipo           = models.CharField(max_length=20, choices=TIPO_CHOICES)
    materia        = models.CharField(max_length=255)
    desc           = models.TextField(blank=True)
    prioridad      = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='Media')
    fecha          = models.DateField(null=True, blank=True)
    horas_est      = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_comp     = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    estado         = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    class Meta:
        indexes = [
            models.Index(fields=['usuario', 'fecha']),
            models.Index(fields=['usuario', 'estado']),
        ]

    def __str__(self):
        return self.titulo
    
class Subtarea(models.Model):
    actividad = models.ForeignKey(
        Actividad,
        on_delete=models.CASCADE,
        related_name='subtareas'
    )

    nombre = models.CharField(max_length=255)
    fecha_entrega = models.DateField()
    horas_estimadas = models.DecimalField(max_digits=5, decimal_places=2)
    done = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['actividad', 'fecha_entrega']),
            models.Index(fields=['fecha_entrega']),
        ]

    def __str__(self):
        return self.nombre


class UserProfile(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    limite_diario_horas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=6.00,
        help_text="Límite de horas estimadas por día (1-16 horas)",
        validators=[
            MinValueValidator(1, message="El límite debe ser al menos 1 hora"),
            MaxValueValidator(16, message="El límite no puede exceder 16 horas")
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"Perfil de {self.usuario.email}"

    def actualizar_limite(self, nuevas_horas):
        """Actualizar el límite diario de horas (1-16)"""
        from decimal import Decimal
        nuevas_horas = Decimal(str(nuevas_horas))
        if nuevas_horas < 1:
            raise ValueError("El límite debe ser al menos 1 hora")
        if nuevas_horas > 16:
            raise ValueError("El límite no puede exceder 16 horas")
        self.limite_diario_horas = nuevas_horas
        self.save()
        return self

