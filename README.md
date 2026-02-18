# Despliegue en Vercel y Render (Frontend + Backend)

Este repositorio es una guía práctica para aprender a estructurar, dockerizar y desplegar una aplicación web siguiendo los principios de **CI/CD** con **GitHub Actions**, **Vercel** y **Render**.

Este proyecto utiliza:

- **Frontend:** Vue 3 + Vite + Tailwind CSS
- **Backend:** FastAPI (Python)
- **Desarrollo:** Docker Compose
- **Despliegue:** GitHub Actions + Render + Vercel

## ¿Qué son Vercel y Render?

**[Vercel](https://vercel.com)** es una plataforma de despliegue para frontend optimizada para Vue, React, Next.js, etc. Ofrece despliegue automático, CDN global y baja latencia.

**[Render](https://render.com)** es una plataforma de despliegue para backend, APIs y bases de datos. Maneja automáticamente SSL, escalado e infraestructura.

En este proyecto usaremos **Vercel** para el despliegue del frontend (Vue 3) y **Render** para el despliegue del backend (FastAPI).

<!-- --- -->

## Índice

1. [Estructura del Proyecto](#1-estructura-del-proyecto)
2. [Desarrollo local con Docker](#2-desarrollo-local-con-docker)
3. [Estructura del Frontend](#3-estructura-del-frontend)
4. [Estructura del Backend](#4-estructura-del-backend)
5. [Guía de Despliegue (CI/CD)](#5-guía-de-despliegue-cicd)
   - [Despliegue del Backend (Render)](#a-despliegue-del-backend-render)
   - [Despliegue del Frontend (Vercel)](#b-despliegue-del-frontend-vercel)
6. [Conceptos clave](#6-conceptos-clave)
7. [Tecnologías utilizadas](#7-tecnologías-utilizadas)
8. [Comandos útiles durante el desarrollo](#8-comandos-útiles-durante-el-desarrollo)
9. [Próximos pasos](#9-próximos-pasos)
10. [Licencia](#licencia)

<!-- --- -->

## 1. Estructura del Proyecto

El repositorio está organizado siguiendo el patrón de monorepositorio sencillo, donde cada servicio tiene su propia responsabilidad y configuración:

```text
.
├── backend/                # API REST con FastAPI (Python)
│   ├── main.py             # Lógica de la API y configuración de CORS
│   ├── requirements.txt    # Dependencias del proyecto
│   └── Dockerfile          # Imagen optimizada para producción (Multi-stage)
├── frontend/               # Aplicación Web con Vue 3 + Vite
│   ├── src/
│   │   ├── App.vue         # Componente principal
│   │   ├── main.ts         # Punto de entrada
│   │   ├── style.css       # Estilos globales con Tailwind
│   │   └── services/
│   │       └── api.ts      # Servicio para consumir API del backend
│   ├── index.html          # Punto de entrada HTML
│   ├── Dockerfile          # Imagen optimizada (Multi-stage)
│   ├── vite.config.ts      # Configuración de Vite
│   └── tailwind.config.js  # Configuración de Tailwind CSS
├── .github/workflows/      # Automatización (CI/CD)
│   ├── deploy-backend.yaml # Despliegue automático a Render
│   └── deploy-frontend.yaml# Despliegue automático a Vercel
├── compose.yaml            # Orquestación para desarrollo local
└── README.md               # Esta documentación
```

<!-- --- -->

## 2. Desarrollo Local con Docker

Para asegurar que todos los desarrolladores trabajen en el mismo entorno, utilizamos **Docker Compose**. Esto emula cómo funcionará la aplicación en producción.

### Requisitos:

- Docker y Docker Compose instalados.

### Pasos:

1. Clona el repositorio.
2. Desde la raíz, levanta ambos servicios:
   ```bash
   docker compose up --build
   ```
3. Accede a las aplicaciones:
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **Backend API:** [http://localhost:8000](http://localhost:8000)
   - **Documentación Interactiva (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

<!-- --- -->

## 3. Estructura del Frontend

### Componentes principales:

- **App.vue:** Componente raíz que consume datos del backend
- **services/api.ts:** Servicio centralizador para peticiones HTTP con axios
- **style.css:** Estilos globales usando Tailwind CSS

### Consumiendo datos del backend:

```typescript
// src/services/api.ts
import { apiService } from './services/api'

// En el componente
onMounted(async () => {
  const data = await apiService.getData()
  // Usar los datos
})
```

### Variables de entorno:

```bash
# Durante desarrollo
VITE_API_URL=http://localhost:8000

# En producción (Render)
VITE_API_URL=https://tu-api.onrender.com
```

<!-- --- -->

## 4. Estructura del Backend

### Endpoints disponibles:

- **GET /** - Estado del backend
- **GET /api/data** - Lista de módulos del proyecto
- **GET /docs** - Documentación interactiva (Swagger)

### CORS configurado:

El backend permite peticiones desde cualquier origen (configurable en producción):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, restringir a dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

<!-- --- -->

## 5. Guía de Despliegue (CI/CD)

El objetivo es que cada vez que hagas un `git push` a la rama `main`, la aplicación se actualice automáticamente en internet.

### A. Despliegue del Backend (Render)

**Configuración para el despliegue automático con GitHub**

1. Ve a [Render.com](https://render.com) e inicia sesión, o crea una cuenta con GitHub.
2. Haz clic en **"New +"** > **"Web Service"**.
3. Conecta tu repositorio de GitHub:
   - Selecciona tu repositorio (`vercel-render`).
   - Haz clic en **"Connect"**.
4. Configura el servicio:
   - **Name:** `vercel-render-backend`
   - **Root Directory:** `./backend` (importante)
   - **Runtime:** `Docker`
   - **Region:** Elige la más cercana a ti
   - **Plan:** Free (o el que prefieras)
5. Haz clic en **"Create Web Service"** y espera a que se despliegue.
6. Una vez desplegado, tu backend estará disponible en una URL como: `https://vercel-render-backend-xxx.onrender.com`

**Configurar Deploy Hook para despliegue automático:**

7. En el dashboard de Render, ve a tu servicio > **Settings**.
8. Busca la sección **"Deploy Hook"** y copia la URL completa.
9. Ve a tu repositorio en GitHub > **Settings** > **Secrets and variables** > **Actions**.
10. Crea un nuevo Secret:
    - **Name:** `RENDER_DEPLOY_HOOK`
    - **Value:** Pega la URL de Render copiada en el paso 8
11. Haz clic en **"Add secret"**.

**¿Qué sucede ahora?**
- Cada vez que hagas `git push` a la rama `main`, GitHub dispara automáticamente el Deploy Hook de Render.
- Render recibe la notificación y comienza un nuevo despliegue.
- Tu backend se actualiza en internet en 1-2 minutos.

**Verifica que funciona:**
- En GitHub, ve a **Actions** después de hacer push.
- Verás los workflows ejecutándose y llamando al Deploy Hook de Render.
- En Render Dashboard, verás nuevos despliegues iniciándose automáticamente.

<!-- --- -->

### B. Despliegue del Frontend (Vercel)

**Despliegue automático mediante GitHub Actions:**

1. Ve a [Vercel.com](https://vercel.com) e inicia sesión (o crea una cuenta con GitHub).
2. Haz clic en **"Add New"** > **"Project"**.
3. Conecta tu repositorio de GitHub:
   - Selecciona tu repositorio (`vercel-render`).
   - Haz clic en **"Import"**.
4. Configura el proyecto:
   - **Project Name:** `vercel-render-frontend` (o el que prefieras)
   - **Root Directory:** `./frontend` (importante, señala la carpeta del frontend)
   - **Framework Preset:** `Vite`
   - **Build Command:** `npm run build` (Vercel lo detecta automáticamente)
   - **Output Directory:** `dist`
5. Configura las variables de entorno:
   - En la sección **"Environment Variables"**, agrega:
     - **Name:** `VITE_API_URL`
     - **Value:** `https://tu-backend.onrender.com` (reemplaza con tu URL de Render)
6. Haz clic en **"Deploy"** y espera a que termine.
7. Una vez desplegado, tu frontend estará disponible en una URL como: `https://vercel-render-frontend-xxx.vercel.app`

**Obtener el token de Vercel para GitHub Actions CI/CD:**

8. Ve a [Vercel Settings > Tokens](https://vercel.com/account/tokens).
9. Haz clic en **"Create"**.
10. Asigna un nombre descriptivo (ej: `GitHub CI/CD`).
11. Selecciona el scope: **Full Account**
12. Haz clic en **"Create Token"** y copia el token completo.

**Configurar el token en GitHub Secrets:**

13. Ve a tu repositorio en GitHub > **Settings** > **Secrets and variables** > **Actions**.
14. Crea un nuevo Secret:
    - **Name:** `VERCEL_TOKEN`
    - **Value:** Pega el token de Vercel copiado
15. Haz clic en **"Add secret"**.

**¿Qué sucede ahora?**
- El workflow `deploy-frontend.yaml` ya está configurado en `.github/workflows/`
- Cada vez que hagas `git push` a la rama `main` (cambios en `frontend/**`), GitHub Actions ejecutará el despliegue
- Vercel recibe los comandos y despliega tu aplicación automáticamente
- Los cambios se verán en la web en 2-3 minutos

**Verifica que funciona:**
- En GitHub, ve a **Actions** después de hacer push
- Verás el workflow `Deploy Frontend to Vercel` ejecutándose
- En Vercel Dashboard, verás nuevos despliegues iniciándose automáticamente

<!-- --- -->

## 6. Conceptos clave

### Docker Multi-stage

En los `Dockerfile`, utilizamos dos o más fases:
- **Builder:** Instala dependencias y compila/construye la aplicación
- **Runner/Development:** Solo copia lo necesario para ejecutar

Esto reduce el tamaño de las imágenes, mejora la seguridad y acelera el despliegue.

### CORS (Cross-Origin Resource Sharing)

El backend está configurado para aceptar peticiones del frontend. Sin esto, el navegador bloquearía la conexión por seguridad.

```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

### Variables de entorno

- **Frontend:** `VITE_API_URL` indica dónde está el backend
- **Backend:** `PORT` indica en qué puerto escuchar

Nunca incluyas estas en el código, usa siempre archivos `.env` (no versionados).

### Secrets de GitHub

Nunca subas contraseñas, tokens o claves al repositorio. Usa siempre:
- GitHub Secrets (Settings > Secrets and variables)
- Variables de entorno en plataformas de despliegue (Vercel, Render)

<!-- --- -->

## 7. Tecnologías utilizadas

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| **Frontend** | Vue 3 | ^3.4.21 |
| **Build Tool** | Vite | ^5.0.11 |
| **CSS** | Tailwind CSS | ^3.4.1 |
| **Backend** | FastAPI | Última |
| **Python** | Python | 3.11+ |
| **Servidor Docker** | Node.js | 20-slim |
| **Base de Datos** | - | (Puede agregarse) |

<!-- --- -->

## 8. Comandos útiles durante el desarrollo

```bash
# Desarrollo local
docker compose up --build

# Detener servicios
docker compose down

# Reconstruir solo frontend
docker compose up --build frontend

# Ver logs de un servicio específico
docker compose logs -f frontend

# Ejecutar comando en un contenedor
docker compose exec frontend npm install
```

<!-- --- -->

## 9. Próximos pasos

- [ ] Agregar autenticación con JWT
- [ ] Implementar base de datos (PostgreSQL)
- [ ] Crear modelos de datos más complejos
- [ ] Escribir tests (pytest para backend, Vitest para frontend)
- [ ] Configurar monitoring y logging
- [ ] Documentar APIs con OpenAPI/Swagger

<!-- --- -->

## 10. Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.