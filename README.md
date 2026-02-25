# Proyecto Integrador

## Estructura del Proyecto

El proyecto está organizado en dos directorios principales:

### Backend
Carpeta del backend con Django
- `src/` - Código fuente del backend
  - `config/` - Archivos de configuración
  - `controllers/` - Controladores
  - `middleware/` - Middleware
  - `models/` - Modelos de datos
  - `routes/` - Rutas

### Frontend
Carpeta del frontend con React + TypeScript + Vite:
- `src/` - Código fuente del frontend
  - `pages/` - Páginas
  - `components/` - Componentes reutilizables
  - `assets/` - Archivos estáticos

## Instalación y Ejecución

### Backend
```bash
cd backend
npm install
npm run dev
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Scripts

### Backend
- `npm run dev` - Inicia el servidor en modo desarrollo con watch
- `npm start` - Inicia el servidor en modo producción

### Frontend
- `npm run dev` - Inicia el servidor de desarrollo
- `npm run build` - Compila el proyecto para producción
- `npm run lint` - Ejecuta eslint
- `npm run preview` - Preview del build de producción
