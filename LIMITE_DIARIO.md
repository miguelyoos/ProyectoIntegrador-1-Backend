# Regulación del Límite Diario - Documentación

## 1. El Problema

### Contexto
Un estudiante universitario tiene múltiples asignaturas y tareas con diferentes fechas de entrega. Sin un control adecuado, podría agendar de forma desorganizada todas sus tareas en un solo día, creando una carga de trabajo imposible de cumplir.

### Escenario Problemático
```
Lunes 25 de Abril:
- Tarea 1: 3 horas
- Tarea 2: 5 horas
- Subtarea A: 2 horas
- Subtarea B: 4 horas
_____________________
Total: 14 horas en un día

Límite diario recomendado: 6 horas
⚠️ SOBRECARGA: 8 horas adicionales
```

### Impacto
- **Estrés académico**: Presión injustificada
- **Falta de realismo**: Imposible terminar todo en un día
- **Mala planificación**: No hay distribución del trabajo
- **Bajo rendimiento**: Calidad comprometida

---

## 2. La Solución: Validación de Límite Diario

### Concepto
Cada usuario tiene un **límite diario de horas estimadas** que define cuántas horas de trabajo estimadas puede tener en un día calendario. El sistema valida este límite en **BACKEND** (no en frontend) para garantizar integridad de datos.

### Rango Permitido
- **Mínimo**: 1 hora
- **Máximo**: 16 horas
- **Default**: 6 horas
- **Personalizable**: Cada usuario puede ajustar su límite

### ¿Por qué en Backend?

| Aspecto | Razón |
|--------|-------|
| **Seguridad** | Frontend puede ser bypasseado (F12, modificar JS) |
| **Integridad** | Garantiza que BD solo tenga datos válidos |
| **Consistencia** | Una única fuente de verdad |
| **API** | Protege la API de clientes maliciosos |
| **Auditoría** | Se registra el intento de violación |

---

## 3. Arquitectura de la Solución

### Componentes

```
┌─────────────────────────────────────────────────────┐
│                   CLIENTE (Frontend)                │
│  Muestra advertencias preventivas al usuario        │
│  Impide UI si límite está cerca del tope           │
└─────────────────┬─────────────────────────────────┘
                  │ HTTP Request
                  ▼
┌─────────────────────────────────────────────────────┐
│              REST API (Backend - Django)            │
│                                                     │
│  1. Recibe request (crear/actualizar tarea)       │
│  2. Obtiene usuario autenticado                    │
│  3. Calcula horas totales del día                 │
│  4. Valida contra límite diario                   │
│  5. Rechaza o acepta la operación                 │
└─────────────────┬─────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│              BASE DE DATOS (PostgreSQL)             │
│                                                     │
│  - UserProfile (limite_diario_horas)              │
│  - Actividad (horas_est, fecha)                   │
│  - Subtarea (horas_estimadas, fecha_entrega)      │
└─────────────────────────────────────────────────────┘
```

### Modelos de Base de Datos

#### UserProfile
```python
class UserProfile(models.Model):
    usuario              # OneToOneField(User)
    limite_diario_horas  # DecimalField(default=6.00)
    created_at          # DateTimeField(auto_now_add=True)
    updated_at          # DateTimeField(auto_now=True)
    
    Validadores: 1 ≤ limite_diario_horas ≤ 16
```

#### Actividad
```python
class Actividad(models.Model):
    usuario        # ForeignKey(User)
    titulo         # CharField
    fecha          # DateField
    horas_est      # DecimalField
    ... otros campos
```

#### Subtarea
```python
class Subtarea(models.Model):
    actividad           # ForeignKey(Actividad)
    nombre              # CharField
    fecha_entrega       # DateField
    horas_estimadas     # DecimalField
    done                # BooleanField
```

---

## 4. Flujo de Validación

### Scenario 1: Crear Actividad

```
User Input: Crear tarea de 4 horas para 2026-04-25
                    │
                    ▼
┌─────────────────────────────────────────┐
│ Validación en Serializer                │
├─────────────────────────────────────────┤
│ 1. Usuario autenticado: ✓              │
│ 2. Campos obligatorios: ✓              │
│ 3. Obtener límite diario: 6 horas      │
│ 4. Calcular total del día:             │
│    - Actividades (2026-04-25): 1.5h    │
│    - Subtareas (2026-04-25): 1.5h      │
│    - Nueva: 4h                         │
│    - Total: 7h                         │
│ 5. Comparar: 7h > 6h                   │
│    ❌ RECHAZAR                          │
└─────────────────────────────────────────┘
                    │
                    ▼
        Error (HTTP 400 Bad Request)
        
{
  "horas_est": "Las horas totales para 2026-04-25 
               (7h) excederían el límite diario 
               de 6h. Otras actividades: 1.5h, 
               Subtareas: 1.5h"
}
```

### Scenario 2: Reprogramar Subtarea

```
User Input: Cambiar subtarea de 2026-04-24 (2h) 
            a 2026-04-25 (5h estimadas)
                    │
                    ▼
┌─────────────────────────────────────────┐
│ Validación en Serializer (PATCH)        │
├─────────────────────────────────────────┤
│ 1. Usuario autenticado: ✓              │
│ 2. Subtarea existe: ✓                  │
│ 3. Obtener límite diario: 6 horas      │
│ 4. Calcular total NUEVA fecha:         │
│    - Actividades (2026-04-25): 1.5h    │
│    - Otras subtareas (2026-04-25): 1h  │
│    - Esta subtarea (nueva): 5h          │
│    - Total: 7.5h                       │
│ 5. Comparar: 7.5h > 6h                 │
│    ❌ RECHAZAR                          │
└─────────────────────────────────────────┘
                    │
                    ▼
        Error (HTTP 400 Bad Request)
        
{
  "horas_estimadas": "Las horas totales para 
                      2026-04-25 (7.5h) excederían 
                      el límite diario de 6h. 
                      Otras tareas ese día: 2.5h"
}
```

### Scenario 3: Reprogramación Exitosa

```
User Input: Cambiar subtarea a 2026-04-26 (2.5h)
                    │
                    ▼
┌─────────────────────────────────────────┐
│ Validación en Serializer (PATCH)        │
├─────────────────────────────────────────┤
│ 1. Usuario autenticado: ✓              │
│ 2. Subtarea existe: ✓                  │
│ 3. Obtener límite diario: 6 horas      │
│ 4. Calcular total NUEVA fecha:         │
│    - Actividades (2026-04-26): 0h      │
│    - Otras subtareas (2026-04-26): 0h  │
│    - Esta subtarea (nueva): 2.5h       │
│    - Total: 2.5h                       │
│ 5. Comparar: 2.5h ≤ 6h                 │
│    ✓ ACEPTAR                            │
└─────────────────────────────────────────┘
                    │
                    ▼
        Éxito (HTTP 200 OK)
        
{
  "id": 5,
  "nombre": "Subtarea",
  "fecha_entrega": "2026-04-26",
  "horas_estimadas": "2.50",
  "done": false
}
```

---

## 5. Implementación Técnica

### 5.1 Validación en Modelo (models.py)

```python
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    limite_diario_horas = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=6.00,
        validators=[
            MinValueValidator(1, message="El límite debe ser al menos 1 hora"),
            MaxValueValidator(16, message="El límite no puede exceder 16 horas")
        ]
    )
    
    def actualizar_limite(self, nuevas_horas):
        """Actualizar límite con validación"""
        from decimal import Decimal
        nuevas_horas = Decimal(str(nuevas_horas))
        if nuevas_horas < 1:
            raise ValueError("El límite debe ser al menos 1 hora")
        if nuevas_horas > 16:
            raise ValueError("El límite no puede exceder 16 horas")
        self.limite_diario_horas = nuevas_horas
        self.save()
        return self
```

### 5.2 Validación en Serializer (serializers.py)

```python
class SubtareaSerializer(serializers.ModelSerializer):
    def validate(self, data):
        # Obtener horas y fecha (usando instance si es PATCH)
        horas = data.get("horas_estimadas")
        fecha_entrega = data.get("fecha_entrega")
        
        if self.instance and self.partial:
            if horas is None:
                horas = self.instance.horas_estimadas
            if fecha_entrega is None:
                fecha_entrega = self.instance.fecha_entrega
        
        actividad = data.get("actividad")
        if self.instance and not actividad:
            actividad = self.instance.actividad
        
        # Validar límite diario
        if actividad and fecha_entrega and horas:
            usuario = actividad.usuario
            
            # Obtener límite del usuario
            try:
                limite = usuario.profile.limite_diario_horas
            except UserProfile.DoesNotExist:
                limite = Decimal('6.00')
            
            # Calcular horas totales en la fecha
            otras_subtareas = Subtarea.objects.filter(
                actividad__usuario=usuario,
                fecha_entrega=fecha_entrega
            )
            
            # Excluir esta subtarea si es actualización
            if self.instance:
                otras_subtareas = otras_subtareas.exclude(id=self.instance.id)
            
            total_otras_horas = otras_subtareas.aggregate(
                total=Sum('horas_estimadas')
            )['total'] or Decimal('0')
            
            total_horas = total_otras_horas + Decimal(str(horas))
            
            # Validar
            if total_horas > limite:
                raise serializers.ValidationError({
                    "horas_estimadas": (
                        f"Las horas totales para {fecha_entrega} "
                        f"({total_horas}h) excederían el límite "
                        f"diario de {limite}h. "
                        f"Otras tareas ese día: {total_otras_horas}h"
                    )
                })
        
        return data
```

### 5.3 Cálculo de Horas Totales

Se calcula la suma de:

**Para una fecha específica:**
```python
# Actividades ese día
actividades_horas = Actividad.objects.filter(
    usuario=user,
    fecha=target_date
).aggregate(Sum('horas_est'))

# Subtareas ese día
subtareas_horas = Subtarea.objects.filter(
    actividad__usuario=user,
    fecha_entrega=target_date
).aggregate(Sum('horas_estimadas'))

# Total
total = actividades_horas + subtareas_horas
```

---

## 6. Endpoints Relacionados

### Obtener Límite Actual
```
GET /api/profile/
```
Respuesta:
```json
{
  "limite_diario_horas": "6.00"
}
```

### Cambiar Límite Diario
```
PATCH /api/profile/
```
Request:
```json
{
  "limite_diario_horas": 8
}
```
Validación: 1 ≤ valor ≤ 16

### Crear Actividad (Valida Límite)
```
POST /api/actividades/
```

### Actualizar Actividad (Valida Límite)
```
PATCH /api/actividades/{id}/
```

### Crear Subtarea (Valida Límite)
```
POST /api/subtareas/
```

### **Reprogramar Subtarea (Valida Límite)** ⭐
```
PATCH /api/subtareas/{id}/
```
Request:
```json
{
  "fecha_entrega": "2026-04-30",
  "horas_estimadas": "3.50"
}
```

---

## 7. Casos de Uso

### Caso 1: Estudiante Sobrecargado
**Situación**: Intenta crear 4 tareas de 4 horas cada una para mañana

**Acción del Sistema**:
1. Primera tarea: ✓ Aceptada (4h)
2. Segunda tarea: ✓ Aceptada (4h + 4h = 8h... pero límite es 6h)
3. Sistema rechaza: "Excede límite de 6h"
4. Estudiante redistribuye a otros días ✓

**Beneficio**: Fuerza planificación realista

### Caso 2: Cambio de Planes
**Situación**: Un profesor adelanta el examen, subtarea debe moverse de Viernes a Jueves

**Acción**:
```
PATCH /api/subtareas/5/
{
  "fecha_entrega": "2026-04-24"  // Jueves
}
```

**Validación**:
- Calcula horas para Jueves
- Si suma > límite → rechaza con sugerencia
- Usuario puede reducir horas estimadas o elegir otro día

### Caso 3: Ajustar Expectativas
**Situación**: Usuario se da cuenta que 6 horas es poco

**Acción**:
```
PATCH /api/profile/
{
  "limite_diario_horas": 10
}
```

**Validación**: 1 ≤ 10 ≤ 16 ✓
Límite actualizado

---

## 8. Flujo de Frontend Recomendado

### Arquitectura Frontend-Backend

**Backend (REST API)**:
- ✅ Valida límite diario
- ✅ Rechaza con HTTP 400 si hay conflicto
- ✅ Proporciona mensaje detallado

**Frontend (React/Vue/Angular)**:
- ✅ Captura error HTTP 400
- ✅ Interpreta el mensaje de error
- ✅ Ofrece soluciones al usuario
- ✅ Reintenta con valores modificados

---

### Creación de Tarea

```
Usuario ingresa datos
         │
         ▼
┌──────────────────────────┐
│ Advertencia preventiva:  │
│ "Para esa fecha tienes  │
│ ya 4h, nuevo total: 8h  │
│ (límite: 6h)"           │
└──────────────────────────┘
         │
    ┌────┴────┐
    │          │
    ▼          ▼
[Cambiar]  [Enviar Anyway]
  fecha       │
    │         ▼
    │     Backend valida
    │     ✓ Creado
    │     ❌ Error 400
    │
    ▼
Redistribuir a otro día
```

---

### Reprogramación de Subtarea - Flujo Completo

#### Paso 1: Usuario Intenta Reprogramar
```
Usuario abre subtarea
    │
    ├─ Actualmente: 2026-04-24, 5 horas
    │
    ▼
[Cambiar Fecha] ← Click
    │
    ▼
Selecciona nueva fecha: 2026-04-25
Confirma horas: 5 horas (sin cambios)
    │
    ▼
PATCH /api/subtareas/5/
{
  "fecha_entrega": "2026-04-25",
  "horas_estimadas": 5
}
```

#### Paso 2: Backend Rechaza (Conflicto)
```
Backend valida:
  - Horas en 2026-04-25: 2h (otras)
  - Horas nuevas: 5h
  - Total: 7h
  - Límite: 6h
  - 7h > 6h ❌

HTTP 400 Bad Request
{
  "horas_estimadas": "Las horas totales para 
                      2026-04-25 (7h) excederían 
                      el límite diario de 6h. 
                      Otras tareas ese día: 2h"
}
```

#### Paso 3: Frontend Muestra Diálogo de Soluciones ⭐
```
⚠️  CONFLICTO DE HORARIO

Para 2026-04-25 ya tienes 2 horas de trabajo.
Si agregas esta subtarea (5h), serían 7h.
Límite diario: 6h

┌─────────────────────────────────────────┐
│                                         │
│  📅 CAMBIAR FECHA A OTRO DÍA            │
│  (mostrar sugerencias de días libres)   │
│  - 2026-04-26: 0h disponibles          │
│  - 2026-04-27: 1h disponibles          │
│  - 2026-04-28: 3h disponibles          │
│  [Seleccionar]                          │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  ⏱️  REDUCIR ESTIMACIÓN DE HORAS        │
│  Actual: 5h                             │
│  Máximo permitido: 4h (6h - 2h)        │
│  [Deslizador: ███░░ 4h]                │
│  [Aplicar cambio]                       │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│  ⬆️  AUMENTAR LÍMITE DIARIO             │
│  Actual: 6h  Propuesto: 8h             │
│  (Rango permitido: 1-16 horas)         │
│  [Ir a Configuración]                   │
│                                         │
├─────────────────────────────────────────┤
│  [Cancelar]                             │
└─────────────────────────────────────────┘
```

---

### Detalle de Cada Opción

#### Opción 1: Cambiar Fecha
```
Frontend calcula días disponibles:

Para cada día sin asignar:
  horas_disponibles = limite_diario - total_ese_día

Si el usuario elige 2026-04-26 (0h asignadas):
  PATCH /api/subtareas/5/
  {
    "fecha_entrega": "2026-04-26",
    "horas_estimadas": 5  // sin cambios
  }
  
  Backend valida: 5h ≤ 6h ✓
  HTTP 200 OK - Éxito
```

#### Opción 2: Reducir Estimación
```
Frontend calcula máximo permitido:
  max_permitido = limite_diario - otras_horas_ese_día
  max_permitido = 6 - 2 = 4 horas

Usuario puede seleccionar:
  - 4.0 horas ✓
  - 3.5 horas ✓
  - 3.0 horas ✓
  
Si elige 4.0:
  PATCH /api/subtareas/5/
  {
    "fecha_entrega": "2026-04-25",  // sin cambios
    "horas_estimadas": 4.0          // reducido
  }
  
  Backend valida: 2 + 4 = 6h ≤ 6h ✓
  HTTP 200 OK - Éxito
```

#### Opción 3: Aumentar Límite
```
Frontend muestra:
  Límite actual: 6h
  Posible nuevo: 7h-16h
  
Usuario elige 8h:
  PATCH /api/profile/
  {
    "limite_diario_horas": 8
  }
  
  Backend valida: 1 ≤ 8 ≤ 16 ✓
  HTTP 200 OK - Límite actualizado
  
Ahora reintentar reprogramación:
  PATCH /api/subtareas/5/
  {
    "fecha_entrega": "2026-04-25",
    "horas_estimadas": 5
  }
  
  Backend valida: 2 + 5 = 7h ≤ 8h ✓
  HTTP 200 OK - Éxito
```

---

### Implementación Frontend Pseudocódigo

```javascript
async function reprogramarSubtarea(subtareaId, nuevaFecha, nuevasHoras) {
  try {
    const response = await fetch(`/api/subtareas/${subtareaId}/`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        fecha_entrega: nuevaFecha,
        horas_estimadas: nuevasHoras
      })
    });
    
    if (response.ok) {
      // ✓ Éxito
      mostrarToast('Subtarea reprogramada correctamente');
      refrescarLista();
      return;
    }
    
    if (response.status === 400) {
      const error = await response.json();
      
      // Capturar mensaje de error del backend
      const mensajeError = error.horas_estimadas || 
                          error.fecha_entrega || 
                          'Error desconocido';
      
      // ⭐ MOSTRAR DIÁLOGO CON OPCIONES
      mostrarDialogoConflictoHorario({
        mensaje: mensajeError,
        limiteDiario: profile.limite_diario_horas,
        fechaSeleccionada: nuevaFecha,
        horasSeleccionadas: nuevasHoras,
        onOpcionCambiarFecha: () => mostrarSelectorFechas(),
        onOpcionReducirHoras: () => mostrarSelectorHoras(),
        onOpcionAumentarLimite: () => navigarASettings()
      });
    }
    
  } catch (error) {
    console.error('Error:', error);
    mostrarError('Error al comunicarse con el servidor');
  }
}
```

---

## 9. Reglas de Validación Resumidas

| Operación | Validación | Dónde |
|-----------|-----------|-------|
| POST /actividades | Horas + día = suma ≤ límite | Backend (Serializer) |
| PATCH /actividades | Horas + día = suma ≤ límite | Backend (Serializer) |
| POST /subtareas | Horas + día = suma ≤ límite | Backend (Serializer) |
| PATCH /subtareas | Horas + día = suma ≤ límite | Backend (Serializer) |
| PATCH /profile | 1 ≤ limite ≤ 16 | Backend (Model + Serializer) |

---

## 10. Mensajes de Error

### Error de Límite Excedido
```json
{
  "horas_estimadas": "Las horas totales para 2026-04-25 (7h) excederían el límite diario de 6h. Otras actividades: 1.5h, Subtareas: 1.5h"
}
```

### Error de Rango de Límite
```json
{
  "limite_diario_horas": "El límite diario no puede exceder 16 horas."
}
```

### Error de Horas Estimadas Inválidas
```json
{
  "horas_estimadas": "Las horas estimadas deben ser mayores a 0."
}
```

---

## 11. Conclusión

La regulación del límite diario es un mecanismo de **validación en backend** que:
- ✅ Garantiza integridad de datos
- ✅ Fuerza planificación realista
- ✅ Protege contra cambios malintencionados
- ✅ Proporciona mensajes claros al usuario
- ✅ Permite redistribución inteligente de tareas

El **frontend** complementa con UX mejorada (advertencias, sugerencias) pero el **backend siempre tiene la palabra final** en cuanto a validez de datos.
