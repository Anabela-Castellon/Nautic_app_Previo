# Nautic

Aplicación web que ayuda a deportistas náuticos a decidir **dónde y cuándo salir al agua**. Reúne el pronóstico de cada spot en un mapa interactivo y le da a cada deporte un **puntaje** según las condiciones del día. También funciona como directorio de escuelas, instructores y negocios de la zona.

Proyecto MVP desarrollado en grupo para el **Seminario de Gestión de Tecnología** (Ingeniería en Informática, UADE).

> **Este repositorio es la copia que preparé para mi defensa individual.** El proyecto original del grupo (`Nautic_app`) no se modificó. La diferencia está explicada en [Qué cambié respecto del original](#qué-cambié-respecto-del-original).

---

## Qué hace

**Usuario (deportista o turista)**
- Mapa con los spots y filtros por deporte.
- Pronóstico a 7 días y puntaje de cada deporte para cada día.
- Mapa con los negocios activos: al hacer clic se ven rubro, dirección, teléfono y horarios.

**Dueño de negocio**
- Registro de cuenta y de su negocio (queda *pendiente* hasta que el administrador lo apruebe).
- Edición de los datos y horarios del negocio.
- **Pausar o reactivar** el negocio: un negocio pausado deja de verse en el mapa.

**Administrador**
- Aprobar o rechazar negocios pendientes y ver todos los negocios.
- Gestionar deportes: crear (con sus condiciones de pronóstico e ícono PNG), activar, desactivar y **eliminar**.
- Gestionar spots: crear, activar y desactivar.

### Cómo se calcula el puntaje

Cada deporte define rangos por variable meteorológica (operadores `between`, `min` y `max`), por ejemplo viento, altura de olas o temperatura. El sistema compara esos rangos con el pronóstico de cada spot y día, y obtiene el puntaje (lógica en `BackEnd/app/services/SportsWeighting.py`). Por eso se puede crear un deporte nuevo desde el panel de administración sin tocar código.

---

## Tecnologías

| Parte | Tecnologías |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy 2.0 |
| Frontend | React 18, Vite, Tailwind CSS, daisyUI, react-leaflet |
| Base de datos | **SQLite** en esta copia · PostgreSQL en el proyecto original |
| Datos de clima | Datos de muestra en esta copia · Google Weather y StormGlass en el original |

---

## Cómo levantarlo (Windows)

Requisitos: **Python 3** (comando `py`) y **Node.js**. La primera vez necesita internet para instalar las dependencias.

1. Doble clic en `start_demo.bat`.
2. El script prepara el entorno, carga los datos de muestra, calcula los puntajes y abre dos ventanas (Backend y Frontend). **No las cierres** mientras uses la app.
3. Se abre el navegador en <http://localhost:5173>. El backend corre en <http://localhost:8000>.

Cada vez que se ejecuta, las fechas del clima de muestra se regeneran a partir de **hoy**, así que siempre hay pronóstico para los próximos 7 días. Los usuarios, negocios y deportes que crees se conservan. Para volver al estado inicial:

```
cd BackEnd
venv\Scripts\python.exe -m app.demo.seed_demo --reset
```

### Instalación manual (Mac, Linux o si falla el `.bat`)

```
# Backend (terminal 1)
cd BackEnd
python -m venv venv
venv\Scripts\activate            # en Mac/Linux: source venv/bin/activate
pip install -r requirements_demo.txt
python -m app.demo.seed_demo
python -m uvicorn app.main:app --port 8000

# Frontend (terminal 2)
cd FrontEnd
npm install
npm run dev
```

Después abrí <http://localhost:5173>. El mapa de fondo (OpenStreetMap) se descarga de internet, así que necesita conexión.

### Cuentas de prueba

| Rol | Email | Contraseña |
|---|---|---|
| Administrador | `admin@admin.com` | `admin` |
| Dueño | `user@user.com` | `user` |
| Dueño con negocio activo | `laura@example.com` | `laura123` |
| Dueño con negocio pendiente | `marina@example.com` | `marina123` |

---

## Qué cambié respecto del original

Para poder mostrar el proyecto en una sola computadora, sin internet ni claves de API:

- **Base de datos:** SQLite local (`BackEnd/nautic_demo.db`) en lugar de PostgreSQL. Las tablas y relaciones son las mismas.
- **Clima:** pronóstico de **muestra** a 7 días para 8 spots (728 registros), en lugar de consultar las APIs. El motor de puntajes es el real; solo cambia el origen de los datos. Archivo: `BackEnd/app/demo/seed_demo.py`.
- **Arranque:** `start_demo.bat` deja todo funcionando con un solo clic.

Mejoras y correcciones agregadas en esta copia:

- Íconos PNG por deporte, que se muestran como marcadores en el mapa.
- Filtros dinámicos por deporte en el mapa.
- Ventana emergente del negocio con sus datos de contacto.
- Botón **Eliminar** deporte en el panel de administración.
- Botón **Pausar / Reactivar** negocio para el dueño. Un negocio pendiente no puede activarse por su cuenta.
- Corrección del rechazo de negocios por parte del administrador.

---

## Limitaciones conocidas

- El clima de esta copia es **de muestra**, no es en tiempo real.
- Alertas por mail y cambio de unidades de medida: no implementados (quedaron fuera del MVP).
- Panel de dueños con pagos y suscripciones reales: no implementado.
- Un dueño con negocio pendiente puede iniciar sesión; su negocio no aparece en el mapa hasta que el administrador lo apruebe.
- Las contraseñas de la base de demo se guardan en texto plano. Es una limitación de la demo, no algo apto para producción.

---

## Estructura

```
BackEnd/
  app/api/        rutas de la API (admin, dueños, spots, deportes, usuarios)
  app/models/     modelos SQLAlchemy
  app/services/   clima y ponderación de deportes
  app/demo/       datos de muestra (seed_demo.py)
  nautic_demo.db  base SQLite
FrontEnd/
  src/components/ y src/pages/   pantallas de la aplicación
  src/api/                       llamadas al backend
start_demo.bat    arranque con un clic
LEEME_DEMO.md     guía corta de la versión demo
```

---

## Autoría

- **Proyecto grupal Nautic:** equipo de 10 personas del Seminario de Gestión de Tecnología (UADE).
- **Esta copia y la defensa individual:** Anabela Castellón (Frontend UI Dev en el equipo).
