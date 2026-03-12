# Proyecto Integrador - Backend

API REST construida con Django + Django REST Framework para gestionar actividades, subtareas y autenticacion JWT.

## Requisitos

- Python 3.12+
- PostgreSQL (o la base configurada en variables de entorno)

## Estructura

- `api/`: modelos, serializers, views y rutas de la API.
- `backend/`: configuracion principal del proyecto Django.
- `manage.py`: comandos de administracion.
- `requirements.txt`: dependencias del backend.

## Instalacion

1. Instalar dependencias:

```bash
pip install -r requirements.txt
```

2. Crear archivo `.env` en la raiz del proyecto:

```env
DEBUG=True
SECRET_KEY=tu_secret_key
DB_NAME=postgres
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=tu_host
DB_PORT=5432
```

3. Ejecutar migraciones:

```bash
python manage.py migrate
```

4. Levantar servidor:

```bash
python manage.py runserver
```

## Autenticacion JWT

La API usa SimpleJWT.

- `POST /api/register/`: registro de usuario (publico, no requiere token).
- `POST /api/login/`: login por email y password (publico).
- `POST /api/refresh/`: renovar access token con refresh token (publico).
- `POST /api/logout/`: invalida refresh token (requiere token).

### Ejemplo login

Request:

```json
{
  "email": "usuario@correo.com",
  "password": "12345678"
}
```

Response:

```json
{
  "user": {
    "id": 1,
    "email": "usuario@correo.com",
    "username": "usuario",
    "first_name": "",
    "last_name": ""
  },
  "refresh": "...",
  "access": "..."
}
```

## Endpoints principales

- `GET|POST /api/actividades/` (protegido)
- `GET|POST /api/subtareas/` (protegido)
- `GET /api/hoy/` (protegido)

## Vista Hoy (`/api/hoy/`)

Entrega subtareas agrupadas y ordenadas por prioridad:

1. Vencidas (fecha mas antigua primero).
2. Para hoy.
3. Proximas (fecha mas cercana primero).
4. Empate por menor esfuerzo estimado (`horas_estimadas`).

Respuesta incluye:

- `regla`: texto en 2-4 lineas para mostrar en UI.
- `vencidas`, `para_hoy`, `proximas`: listas agrupadas.
- `vacia`: `true/false` para estado vacio.
- `accion`: sugerencia de UX (`Crear actividad`) cuando no hay datos.

### Filtros soportados

- `materia`: filtra por curso/materia.
- `estado`: filtra por estado de actividad.

Ejemplo:

```http
GET /api/hoy/?materia=Matematicas&estado=pendiente
Authorization: Bearer <access_token>
```

## Seguridad y proteccion de rutas

- Configuracion global en DRF: `IsAuthenticated`.
- Excepciones publicas: `register`, `login` y `refresh`.
- Filtrado por usuario autenticado en queries para evitar exponer datos de otros usuarios.

## Comandos utiles

- `python manage.py check`: validar configuracion.
- `python manage.py makemigrations`
- `python manage.py migrate`
- `python manage.py runserver`
