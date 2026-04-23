# Documentación de Endpoints - API Proyecto Integrador

## Autenticación

### 1. Registro de Usuario
**POST** `/api/register/`

Registra un nuevo usuario en el sistema. Automáticamente crea un perfil con límite diario de 6 horas.

**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "miPassword123",
  "username": "miusuario",
  "first_name": "Juan",
  "last_name": "Pérez"
}
```

**Response (201 Created):**
```json
{
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "username": "miusuario",
    "first_name": "Juan",
    "last_name": "Pérez"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Validaciones:**
- Email debe ser único (case-insensitive)
- Password mínimo 8 caracteres
- Email es obligatorio

---

### 2. Login
**POST** `/api/login/`

Autentica un usuario con email y contraseña.

**Request:**
```json
{
  "email": "usuario@example.com",
  "password": "miPassword123"
}
```

**Response (200 OK):**
```json
{
  "user": {
    "id": 1,
    "email": "usuario@example.com",
    "username": "miusuario",
    "first_name": "Juan",
    "last_name": "Pérez"
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Errores:**
- 400: Credenciales incorrectas

---

### 3. Refresh Token
**POST** `/api/refresh/`

Obtiene un nuevo access token usando el refresh token.

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Logout
**POST** `/api/logout/`

Cierra la sesión invalidando el refresh token.

**Permisos:** Requiere autenticación (token JWT)

**Request:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (205 Reset Content):**
```json
{
  "detail": "Sesión cerrada correctamente"
}
```

**Errores:**
- 400: Token inválido

---

## Perfil de Usuario

### 5. Obtener Perfil
**GET** `/api/profile/`

Obtiene el perfil del usuario autenticado con su límite diario.

**Permisos:** Requiere autenticación (token JWT)

**Response (200 OK):**
```json
{
  "id": 1,
  "usuario": 1,
  "limite_diario_horas": "6.00",
  "created_at": "2026-04-23T10:30:00Z",
  "updated_at": "2026-04-23T10:30:00Z"
}
```

---

### 6. Actualizar Límite Diario
**PATCH** `/api/profile/`

Actualiza el límite diario de horas del usuario.

**Permisos:** Requiere autenticación (token JWT)

**Request:**
```json
{
  "limite_diario_horas": 8
}
```

**Response (200 OK):**
```json
{
  "detail": "Límite diario actualizado correctamente",
  "profile": {
    "id": 1,
    "usuario": 1,
    "limite_diario_horas": "8.00",
    "created_at": "2026-04-23T10:30:00Z",
    "updated_at": "2026-04-23T10:35:00Z"
  }
}
```

**Validaciones:**
- Mínimo: 1 hora
- Máximo: 16 horas

**Errores:**
- 400: Valor fuera de rango

---

## Actividades

### 7. Listar Actividades
**GET** `/api/actividades/`

Lista todas las actividades del usuario autenticado.

**Permisos:** Requiere autenticación

**Query Parameters:**
- `search`: Buscar por título
- `ordering`: Ordenar por campo (ej: `-fecha`)

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "usuario": 1,
    "titulo": "Proyecto Python",
    "tipo": "Proyecto",
    "materia": "Programación",
    "desc": "Implementar un sistema de gestión",
    "prioridad": "Alta",
    "fecha": "2026-05-15",
    "horasEst": 10.5,
    "horasComp": 3.0,
    "estado": "en_progreso",
    "subtareas": [
      {
        "id": 1,
        "actividad": 1,
        "nombre": "Diseñar base de datos",
        "fecha_entrega": "2026-04-30",
        "horas_estimadas": "5.00",
        "done": false
      }
    ]
  }
]
```

---

### 8. Crear Actividad
**POST** `/api/actividades/`

Crea una nueva actividad. Valida que las horas estimadas no superen el límite diario.

**Permisos:** Requiere autenticación

**Request:**
```json
{
  "titulo": "Proyecto Python",
  "tipo": "Proyecto",
  "materia": "Programación",
  "desc": "Implementar un sistema de gestión",
  "prioridad": "Alta",
  "fecha": "2026-05-15",
  "horasEst": 4.0,
  "horasComp": 0,
  "estado": "pendiente"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "usuario": 1,
  "titulo": "Proyecto Python",
  "tipo": "Proyecto",
  "materia": "Programación",
  "desc": "Implementar un sistema de gestión",
  "prioridad": "Alta",
  "fecha": "2026-05-15",
  "horasEst": 4.0,
  "horasComp": 0,
  "estado": "pendiente",
  "subtareas": []
}
```

**Validaciones:**
- `titulo` obligatorio
- `tipo` obligatorio
- `materia` obligatoria
- `horasEst` + otras actividades/subtareas del día ≤ límite diario

**Errores:**
- 400: Validación fallida (límite diario excedido)

---

### 9. Obtener Actividad
**GET** `/api/actividades/{id}/`

Obtiene una actividad específica del usuario.

**Permisos:** Requiere autenticación

**Response (200 OK):**
```json
{
  "id": 1,
  "usuario": 1,
  "titulo": "Proyecto Python",
  "tipo": "Proyecto",
  "materia": "Programación",
  "desc": "Implementar un sistema de gestión",
  "prioridad": "Alta",
  "fecha": "2026-05-15",
  "horasEst": 4.0,
  "horasComp": 0,
  "estado": "pendiente",
  "subtareas": []
}
```

**Errores:**
- 404: Actividad no encontrada

---

### 10. Actualizar Actividad
**PUT** `/api/actividades/{id}/`

Actualiza todos los campos de una actividad.

**Permisos:** Requiere autenticación

**Request:**
```json
{
  "titulo": "Proyecto Python - Actualizado",
  "tipo": "Proyecto",
  "materia": "Programación",
  "desc": "Implementar un sistema mejorado",
  "prioridad": "Urgente",
  "fecha": "2026-05-20",
  "horasEst": 5.0,
  "horasComp": 2.0,
  "estado": "en_progreso"
}
```

**Validaciones:** Igual a crear actividad

---

### 11. Actualizar Parcial Actividad
**PATCH** `/api/actividades/{id}/`

Actualiza parcialmente una actividad.

**Permisos:** Requiere autenticación

**Request:**
```json
{
  "estado": "completada",
  "horasComp": 10.5
}
```

---

### 12. Eliminar Actividad
**DELETE** `/api/actividades/{id}/`

Elimina una actividad y todas sus subtareas.

**Permisos:** Requiere autenticación

**Response (204 No Content)**

---

## Subtareas

### 13. Listar Subtareas
**GET** `/api/subtareas/`

Lista todas las subtareas del usuario autenticado.

**Permisos:** Requiere autenticación

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "actividad": 1,
    "nombre": "Diseñar base de datos",
    "fecha_entrega": "2026-04-30",
    "horas_estimadas": "5.00",
    "done": false
  }
]
```

---

### 14. Crear Subtarea
**POST** `/api/subtareas/`

Crea una nueva subtarea. Valida límite diario.

**Permisos:** Requiere autenticación

**Request:**
```json
{
  "actividad": 1,
  "nombre": "Diseñar base de datos",
  "fecha_entrega": "2026-04-30",
  "horas_estimadas": "5.00",
  "done": false
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "actividad": 1,
  "nombre": "Diseñar base de datos",
  "fecha_entrega": "2026-04-30",
  "horas_estimadas": "5.00",
  "done": false
}
```

**Validaciones:**
- `nombre` obligatorio
- `fecha_entrega` obligatoria
- `horas_estimadas` > 0
- Total de horas en esa fecha ≤ límite diario

**Errores:**
- 400: Validación fallida

---

### 15. Obtener Subtarea
**GET** `/api/subtareas/{id}/`

Obtiene una subtarea específica.

**Permisos:** Requiere autenticación

**Response (200 OK):**
```json
{
  "id": 1,
  "actividad": 1,
  "nombre": "Diseñar base de datos",
  "fecha_entrega": "2026-04-30",
  "horas_estimadas": "5.00",
  "done": false
}
```

---

### 16. Reprogramar Subtarea (Cambiar Fecha y/o Horas)
**PATCH** `/api/subtareas/{id}/`

Actualiza la fecha de entrega y/o horas estimadas de una subtarea. Esta es la operación principal para reprogramación.

**Permisos:** Requiere autenticación

**Request (Ejemplo 1 - Solo cambiar fecha):**
```json
{
  "fecha_entrega": "2026-05-05"
}
```

**Request (Ejemplo 2 - Solo cambiar horas):**
```json
{
  "horas_estimadas": "3.50"
}
```

**Request (Ejemplo 3 - Cambiar ambas):**
```json
{
  "fecha_entrega": "2026-05-05",
  "horas_estimadas": "3.50"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "actividad": 1,
  "nombre": "Diseñar base de datos",
  "fecha_entrega": "2026-05-05",
  "horas_estimadas": "3.50",
  "done": false
}
```

**Validaciones:**
- `horas_estimadas` debe ser > 0 (si se proporciona)
- Total de horas en nueva fecha ≤ límite diario
- Si hay conflicto de límite diario, rechaza con error detallado

**Errores:**
- 400: Horas exceden límite diario
  ```json
  {
    "horas_estimadas": "Las horas totales para 2026-05-05 (8h) excederían el límite diario de 6h. Otras tareas ese día: 3h"
  }
  ```

---

### 17. Actualizar Completa Subtarea
**PUT** `/api/subtareas/{id}/`

Actualiza todos los campos de una subtarea.

**Permisos:** Requiere autenticación

**Request:**
```json
{
  "actividad": 1,
  "nombre": "Diseñar base de datos v2",
  "fecha_entrega": "2026-05-05",
  "horas_estimadas": "3.50",
  "done": false
}
```

---

### 18. Eliminar Subtarea
**DELETE** `/api/subtareas/{id}/`

Elimina una subtarea.

**Permisos:** Requiere autenticación

**Response (204 No Content)**

---

## Vista Especial

### 19. Vista Hoy
**GET** `/api/hoy/`

Obtiene las subtareas organizadas por estado: vencidas, para hoy y próximas.

**Permisos:** Requiere autenticación

**Query Parameters:**
- `materia`: Filtrar por materia
- `estado`: Filtrar por estado de la actividad

**Response (200 OK):**
```json
{
  "vacia": false,
  "regla": [
    "1. Vencidas primero: la subtarea con fecha más antigua aparece arriba.",
    "2. Luego las de hoy, ordenadas por menor esfuerzo estimado.",
    "3. Luego Próximas, por fecha más cercana primero.",
    "4. Empate en fecha: se desempata por menor esfuerzo estimado."
  ],
  "vencidas": [
    {
      "id": 1,
      "actividad": 1,
      "nombre": "Tarea vencida",
      "fecha_entrega": "2026-04-20",
      "horas_estimadas": "2.00",
      "done": false
    }
  ],
  "para_hoy": [
    {
      "id": 2,
      "actividad": 2,
      "nombre": "Tarea de hoy",
      "fecha_entrega": "2026-04-23",
      "horas_estimadas": "1.50",
      "done": false
    }
  ],
  "proximas": [
    {
      "id": 3,
      "actividad": 3,
      "nombre": "Tarea próxima",
      "fecha_entrega": "2026-04-25",
      "horas_estimadas": "3.00",
      "done": false
    }
  ]
}
```

**Respuesta cuando no hay tareas:**
```json
{
  "vacia": true,
  "mensaje": "No tienes subtareas para mostrar.",
  "accion": "Crear actividad",
  "regla": [...],
  "vencidas": [],
  "para_hoy": [],
  "proximas": []
}
```

---

## Notas Generales

### Autenticación
Todos los endpoints excepto `register`, `login` y `refresh` requieren:
```
Authorization: Bearer <access_token>
```

### Códigos de Estado
- **200**: Éxito (GET, PATCH, PUT)
- **201**: Recurso creado (POST)
- **204**: Éxito sin contenido (DELETE)
- **205**: Éxito con reset (Logout)
- **400**: Error de validación
- **401**: No autenticado
- **404**: No encontrado
- **409**: Conflicto

### Formato de Fechas
- ISO 8601: `YYYY-MM-DD`
- Ejemplo: `2026-05-15`

### Formato de Decimales
- Máximo 5 dígitos totales
- 2 decimales
- Ejemplo: `10.50`, `1.00`

### Conversión camelCase ↔ snake_case
El API convierte automáticamente:
- Request: `horasEst`, `horasComp` (camelCase)
- Response: Se devuelven en camelCase

Internamente se usan: `horas_est`, `horas_comp` (snake_case)
