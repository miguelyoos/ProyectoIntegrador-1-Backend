# Proyecto Integrador

## Estructura del Proyecto

El proyecto está organizado en dos directorios principales:

### Backend
Carpeta del backend con Django
-`api/`                 # Aplicación principal (modelos, vistas, endpoints)
-`backend/`              # Configuración principal del proyecto Django
-`manage.py`             # Archivo para ejecutar comandos Django
-`requirements.txt`      # Dependencias del proyecto
-`README.md`             # Documentación del backend
INSTALAR:
pip install django
pip install django-rest-framework
pip install psycopg2
pip install django-cors-headers

### Frontend
Carpeta del frontend con React + TypeScript + Vite:
- `src/` - Código fuente del frontend
  - `pages/` - Páginas
  - `components/` - Componentes reutilizables
  - `assets/` - Archivos estáticos

## Instalación y Ejecución

### Backend
```bash
cd Backend
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Scripts

### Backend
- `python manage.py runserver` - Inicia el servidor en modo producción

### Frontend
- `npm run dev` - Inicia el servidor de desarrollo
- `npm run build` - Compila el proyecto para producción
- `npm run lint` - Ejecuta eslint
- `npm run preview` - Preview del build de producción
