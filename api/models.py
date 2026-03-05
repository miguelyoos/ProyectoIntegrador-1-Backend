from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.utils import timezone



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

