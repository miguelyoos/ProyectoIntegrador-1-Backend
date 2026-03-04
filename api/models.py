from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
# from django.contrib.auth.models import BaseUserManager
from django.utils import timezone
from django.conf import settings

from Backend.backend import settings


class Actividad(models.Model):
    usuario = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name='actividades'
    )
    TIPO_CHOICES = [
        ('examen', 'Examen'),
        ('quiz', 'Quiz'),
        ('taller', 'Taller'),
        ('proyecto', 'Proyecto'),
        ('otro', 'Otro'),
        ('tarea', 'Tarea'),
    ]
    prioridad_choices = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
        
    titulo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    materia = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    prioridad = models.CharField(max_length=10, choices=prioridad_choices, default='media')
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    horas_estimadas = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


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



    def __str__(self):
        return self.nombre

# class Usuario(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(unique=True)
#     nombre = models.CharField(max_length=100)

#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     date_joined = models.DateTimeField(default=timezone.now)

#     objects = UsuarioManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['nombre']

#     def __str__(self):
#         return self.email