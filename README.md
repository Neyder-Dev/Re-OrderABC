# ReOrdena-ABC 🏭

> Motor de optimización logística basado en el Algoritmo ABC (Pareto 80/20) para reubicación inteligente de inventario en bodega.

---

## ¿Qué resuelve?

Las bodegas organizadas "a ojo" generan tiempos de caminata innecesarios y errores de picking. **ReOrdena-ABC** analiza los datos reales de ventas y sugiere automáticamente dónde debe vivir cada producto según su rotación, reduciendo el tiempo de despacho al concentrar los productos de alta rotación cerca de las zonas de salida.

---

## Stack Tecnológico

| Capa | Tecnología | Razón |
|---|---|---|
| Backend | Python 3.11 + FastAPI | Validaciones asíncronas de archivos pesados + Swagger autogenerado |
| Procesamiento | Pandas | Motor de limpieza y cálculo de percentiles ABC |
| Frontend | React.js + Tailwind CSS | Componentes dinámicos para el mapa de calor de racks |
| Base de Datos | PostgreSQL | Persistencia del maestro de productos y coordenadas de posiciones |
| Contenedores | Docker + Docker Compose | Ambiente reproducible en cualquier máquina |

---

## Arquitectura del Proyecto

```
reordena-abc/
├── backend/
│   ├── app/
│   │   ├── main.py              # Entry point FastAPI
│   │   ├── core/
│   │   │   ├── config.py        # Variables de entorno
│   │   │   └── database.py      # Conexión PostgreSQL (SQLAlchemy)
│   │   ├── models/              # Modelos ORM (Product, WarehousePosition, etc.)
│   │   ├── schemas/             # Pydantic schemas — validación de entrada/salida
│   │   ├── routers/             # Endpoints agrupados por dominio
│   │   └── services/            # Lógica de negocio (algoritmo ABC, data cleansing)
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Componentes reutilizables (RackMap, HeatCell, etc.)
│   │   ├── pages/               # Vistas principales
│   │   ├── services/            # Llamadas a la API REST
│   │   └── store/               # Estado global (Zustand)
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## Algoritmo ABC — Lógica de Clasificación

El motor clasifica cada SKU según su participación acumulada en las ventas del período analizado:

| Zona | Criterio | Ubicación sugerida | Color en mapa |
|---|---|---|---|
| **A** | Top 20% de ventas (80% del volumen) | Niveles bajos / cerca a despacho | 🔴 Rojo |
| **B** | Siguiente 30% | Niveles medios | 🟡 Amarillo |
| **C** | 50% restante (low movers) | Niveles altos / fondo de bodega | 🟢 Verde |

---

## Pipeline de Datos

```
[CSV/Excel de ventas]
        ↓
[Data Cleansing — Pandas]
  · Normalización de columnas
  · Eliminación de duplicados
  · Manejo de nulos y formatos inconsistentes
        ↓
[Motor ABC]
  · Cálculo de ventas acumuladas por SKU
  · Ordenamiento descendente
  · Asignación de percentiles (A / B / C)
        ↓
[Validación de volumetría]
  · Verificar que el SKU cabe físicamente en la posición sugerida
  · Respetar capacidad por nivel de rack
        ↓
[JSON de sugerencias → Frontend]
  · Mapa de calor de los 3 racks (3 niveles × 1,000 posiciones)
```

---

## Configuración y Arranque

### Pre-requisitos
- Docker y Docker Compose instalados
- Python 3.11+ (para desarrollo local sin Docker)
- Node.js 18+

### Desarrollo local (sin Docker)

```bash
# 1. Clona el repositorio
git clone https://github.com/tu-usuario/reordena-abc.git
cd reordena-abc

# 2. Backend
cd backend
cp .env.example .env          # Edita con tus valores locales
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 3. Frontend (otra terminal)
cd frontend
cp .env.example .env.local    # Edita VITE_API_URL=http://localhost:8000
npm install
npm run dev
```

| Servicio | URL local |
|---|---|
| API REST | http://localhost:8000 |
| Swagger (docs) | http://localhost:8000/docs |
| Frontend | http://localhost:5173 |

---

## Variables de Entorno

### Backend (`backend/.env`)

```env
DATABASE_URL=postgresql://usuario:password@host:5432/reordena_abc
SECRET_KEY=genera-con-openssl-rand-hex-32
ALLOWED_ORIGINS=http://localhost:5173,https://tu-app.vercel.app
ADMIN_EMAIL=admin@reordena.com
ADMIN_PASSWORD=CambiaEstaContrasena2024!
```

> Genera una `SECRET_KEY` segura: `openssl rand -hex 32`

### Frontend (`frontend/.env.local`)

```env
VITE_API_URL=http://localhost:8000
```

---

## Despliegue en Producción

### Backend → Railway

1. Crea un nuevo proyecto en [Railway](https://railway.app)
2. Agrega un servicio **PostgreSQL** — Railway provee `DATABASE_URL` automáticamente
3. Conecta tu repositorio de GitHub al proyecto
4. Railway detecta `railway.json` en la raíz y usa `backend/Dockerfile` automáticamente
5. En **Variables** del servicio agrega:

   | Variable | Valor |
   |---|---|
   | `SECRET_KEY` | Resultado de `openssl rand -hex 32` |
   | `ALLOWED_ORIGINS` | URL de tu frontend en Vercel (ej: `https://reordena-abc.vercel.app`) |
   | `ADMIN_EMAIL` | Tu correo de administrador |
   | `ADMIN_PASSWORD` | Contraseña segura |

6. Una vez desplegado, crea el usuario administrador ejecutando desde Railway Shell:
   ```bash
   python crear_jefe.py
   ```

### Frontend → Vercel

1. Importa el repositorio en [Vercel](https://vercel.com)
2. En la configuración del proyecto:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
3. En **Environment Variables** agrega:

   | Variable | Valor |
   |---|---|
   | `VITE_API_URL` | URL de tu backend en Railway (ej: `https://tu-backend.up.railway.app`) |

4. Vercel detecta `frontend/vercel.json` y configura el routing de la SPA automáticamente

---

## Cronograma — 9 Semanas (Mar 27 – May 29)

| Semana | Foco |
|---|---|
| 1 | Setup del repositorio, modelos de DB, primer endpoint `/health` |
| 2–3 | Ingesta de archivos: `POST /upload`, data cleansing con Pandas |
| 4–5 | Motor ABC: cálculo de percentiles + validación de volumetría |
| 6–7 | Frontend: mapa de calor de racks, visualización de sugerencias |
| 8 | Integración end-to-end, pruebas con datos reales |
| 9 | Ajustes finales, documentación, entrega MVP |

---

## Retos Técnicos Identificados

1. **Data Cleansing**: Los reportes de ventas llegan con columnas inconsistentes, fechas en múltiples formatos, SKUs duplicados con nombres distintos y celdas vacías. El pipeline de limpieza debe ser robusto y auditable.

2. **Validación de volumetría**: La sugerencia del algoritmo debe cruzarse con las dimensiones físicas del producto y la capacidad real de cada nivel del rack antes de presentarse al operario.

---

## Contribuir

1. Crea una rama desde `main`: `git checkout -b feature/nombre-del-feature`
2. Haz commit con mensajes descriptivos en español
3. Abre un Pull Request describiendo el cambio y su impacto

---

*ReOrdena-ABC — Proyecto Universitario · MVP v0.1.0*