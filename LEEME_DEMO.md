# Nautic – copia DEMO para la defensa

Esta carpeta es una **copia** del proyecto original (`Nautic_app`), que no se tocó.
La diferencia: en vez de Postgres + Google Weather + StormGlass, usa una base **SQLite local**
con un pronóstico de **muestra** para los próximos 7 días. El resto del código
(frontend, rutas de la API, cálculo de puntajes por deporte) es el mismo.

## Cómo levantarlo

Doble clic en `start_demo.bat`. Hace todo solo:

1. Prepara el entorno de Python (copia el `venv` de la carpeta original; si no puede, instala con pip, necesita internet).
2. Carga los datos de muestra (`BackEnd/app/demo/seed_demo.py`) y calcula los puntajes por deporte.
3. Levanta el backend en <http://localhost:8000> y el frontend en <http://localhost:5173>.

Cada vez que lo ejecutás, las fechas del clima se regeneran a partir de **hoy**, así que siempre hay datos para el selector de días.
Los usuarios/negocios que crees durante la prueba se conservan; para volver a cero:

```
cd BackEnd
venv\Scripts\python.exe -m app.demo.seed_demo --reset
```

Usuarios de prueba (los mismos de siempre): `user@user.com` / `user` (dueño), `admin@admin.com` / `admin` (admin).

## Qué se cambió respecto al original

| Archivo | Cambio |
|---|---|
| `BackEnd/app/core/config.py` | Si no hay `DATABASE_URL`, usa SQLite local (`nautic_demo.db`) |
| `BackEnd/app/core/database.py` | Acepta SQLite (con Postgres funciona igual que antes) |
| `BackEnd/app/demo/seed_demo.py` (nuevo) | Datos base + clima de muestra + puntajes |
| `start_demo.bat`, `LEEME_DEMO.md` (nuevos) | Arranque y esta guía |

## Para cambiar los valores del clima

Editá el diccionario `PERFILES` en `BackEnd/app/demo/seed_demo.py` (temperatura, viento, olas, etc. por spot) y volvé a ejecutar `start_demo.bat`.

## Para la defensa

El clima que se ve es de muestra, no viene de las APIs reales. Si te preguntan, el flujo real está en `WeatherLogic.py` (Google Weather + StormGlass → tabla `variable_meteorologica` → `SportsWeighting.py`); el demo reemplaza solo la fuente de datos.
