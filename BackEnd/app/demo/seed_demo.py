"""
Carga de datos DEMO para Nautic (sin Postgres ni APIs de clima).

Qué hace:
  1) Crea las tablas (SQLite local, ver .env).
  2) Si la base está vacía, carga los datos base del proyecto (spots, deportes,
     usuarios, negocios, reglas por deporte, tipos de variable...) usando los mismos
     scripts de app/models/db_creation.
  3) Genera un pronóstico de muestra para los próximos 7 días en cada spot
     (reemplaza a Google Weather + StormGlass).
  4) Calcula las ponderaciones por deporte con la lógica REAL del proyecto
     (app/services/SportsWeighting.py).

Uso (desde la carpeta BackEnd):
    python -m app.demo.seed_demo           # conserva usuarios/negocios, refresca el clima
    python -m app.demo.seed_demo --reset   # borra todo y vuelve a cargar desde cero
"""
import random
import sys
from datetime import datetime, timedelta

from sqlalchemy import text

from app.core.database import Base, SessionLocal, engine
from app.models import models as m
from app.models.models import (
    ProveedorDatos, Spot, TipoVariableMeteorologica,
    VariableMeteorologica, DeporteSpot,
)
from app.services.SportsWeighting import ponderar_todos_los_deportes

DIAS = 7  # hoy + 6 (el selector del mapa muestra 5)

# Valores base por spot (día 0). Hay variedad a propósito para que gane un
# deporte distinto según el lugar.
PERFILES = {
    # Surf: poco viento y olas medianas/largas
    "Mar del Plata": dict(tmax=21, tmin=12, wind=6, gust=12, wave=1.8, period=11, water=16, cloud=15, pprob=5, qpf=0.0, uv=7),
    "South Beach": dict(tmax=27, tmin=21, wind=7, gust=13, wave=1.4, period=10, water=25, cloud=15, pprob=5, qpf=0.0, uv=8),
    # Kitesurf: viento sostenido, olas moderadas
    "Praia de Iracema": dict(tmax=31, tmin=25, wind=20, gust=28, wave=1.1, period=8, water=28, cloud=10, pprob=5, qpf=0.0, uv=9),
    "Playa Blanca": dict(tmax=24, tmin=18, wind=22, gust=30, wave=1.5, period=9, water=21, cloud=15, pprob=5, qpf=0.0, uv=6),
    # Kayak: aguas calmas
    "Anse Source d'Argent": dict(tmax=30, tmin=26, wind=1, gust=2, wave=0.05, period=1.5, water=28, cloud=3, pprob=0, qpf=0.0, uv=9),
    "Paralia Navagio": dict(tmax=21, tmin=14, wind=3, gust=6, wave=0.3, period=6, water=19, cloud=15, pprob=5, qpf=0.0, uv=3),
    "Lago Nahuel Huapi": dict(tmax=19, tmin=10, wind=1, gust=2, wave=0.05, period=1.5, water=15, cloud=3, pprob=0, qpf=0.0, uv=7),
    # Frío: contraste (puntajes bajos)
    "Pragser Wildsee": dict(tmax=6, tmin=-1, wind=6, gust=10, wave=0.05, period=2, water=5, cloud=60, pprob=25, qpf=0.5, uv=1),
}
DEFAULT = dict(tmax=24, tmin=15, wind=14, gust=24, wave=0.8, period=7, water=20, cloud=40, pprob=20, qpf=0.3, uv=6)
# Spots nuevos (creados desde la app durante la demo) usan un perfil segun su tipo.
PERFIL_POR_TIPO = {
    "lago": PERFILES["Lago Nahuel Huapi"],
    "playa": PERFILES["Mar del Plata"],
}

# variable -> proveedor (igual que WeatherLogic.PROVIDER_BY_VAR, por nombre real en la tabla)
GOOGLE = "Google Maps Platform"
STORM = "StormGlass"


def _clamp(v, lo, hi):
    return max(lo, min(hi, v))


def _dia(spot: Spot, i: int):
    """Pronóstico de muestra del día i (0 = hoy) para un spot. Determinístico."""
    p = PERFILES.get(spot.nombre) or PERFIL_POR_TIPO.get((spot.tipo or "").strip().lower(), DEFAULT)
    rng = random.Random(f"{spot.codigo}-{i}")
    tmax = p["tmax"] + rng.uniform(-2.5, 2.5)
    tmin = min(p["tmin"] + rng.uniform(-2, 2), tmax - 3)
    wind = _clamp(p["wind"] * rng.uniform(0.8, 1.25), 1, 60)
    gust = max(wind + 1.5, p["gust"] * rng.uniform(0.85, 1.2))
    wave = _clamp(p["wave"] * rng.uniform(0.7, 1.35), 0.05, 6)
    period = _clamp(p["period"] * rng.uniform(0.85, 1.2), 1, 18)
    water = p["water"] + rng.uniform(-1, 1)
    cloud = _clamp(p["cloud"] * rng.uniform(0.5, 2.0) + rng.uniform(0, 8), 0, 100)
    pprob = _clamp(p["pprob"] + rng.uniform(0, 20), 0, 100) if p["pprob"] > 0 else 0
    qpf = round(p["qpf"] * rng.uniform(0.5, 2.0), 1) if pprob > 30 else 0.0
    uv = _clamp(round(p["uv"] + rng.uniform(-1, 1)), 0, 12)
    return {
        "uvIndex": (uv, GOOGLE),
        "precipitation_probability": (round(pprob), GOOGLE),
        "precipitation_qpfCuantity": (qpf, GOOGLE),
        "wind_speed": (round(wind, 1), GOOGLE),
        "wind_gustValue": (round(gust, 1), GOOGLE),
        "cloudCover": (round(cloud), GOOGLE),
        "maxTemperature": (round(tmax, 1), GOOGLE),
        "minTemperature": (round(tmin, 1), GOOGLE),
        "feelsLikeMaxTemperature": (round(tmax - wind * 0.08, 1), GOOGLE),
        "feelsLikeMinTemperature": (round(tmin - wind * 0.1, 1), GOOGLE),
        "waterTemperature": (round(water, 1), STORM),
        "waveHeight": (round(wave, 2), STORM),
        "wavePeriod": (round(period, 1), STORM),
    }


def cargar_base_si_esta_vacia():
    from app.models.db_creation.provider_data import seed_providers
    from app.models.db_creation.sports_data import seed_sports
    from app.models.db_creation.spots_data import seed_spots
    from app.models.db_creation.users_data import seed_users
    from app.models.db_creation.tipoVariable_data import seed_tipo_variable_meteorologica
    from app.models.db_creation.deporteVariable_data import seed_deporte_variable
    from app.models.db_creation.business_data import seed_businesses
    from app.models.db_creation.negocio_deporte import seed_negocio_deportes

    db = SessionLocal()
    vacia = db.query(Spot).count() == 0
    db.close()
    if not vacia:
        print("ℹ️  La base ya tiene datos base; solo se refresca el clima.")
        return

    seed_providers()
    seed_sports()
    seed_spots()
    seed_users()
    seed_tipo_variable_meteorologica(SessionLocal())
    seed_deporte_variable(SessionLocal())
    seed_businesses()
    seed_negocio_deportes()


def normalizar_coordenadas():
    """Postgres guarda lat/lon con 6 decimales (Numeric(10,6)) y SQLite no. La API
    busca el spot por coincidencia exacta de coordenadas, así que redondeamos igual."""
    with engine.begin() as conn:
        for tabla in ("spot", "negocio"):
            conn.execute(text(f"UPDATE {tabla} SET lat = ROUND(lat, 6), lon = ROUND(lon, 6)"))


def refrescar_clima():
    db = SessionLocal()
    try:
        tipos = {t.nombre: t.id for t in db.query(TipoVariableMeteorologica).all()}
        provs = {p.nombre: p.id for p in db.query(ProveedorDatos).all()}
        spots = db.query(Spot).all()

        # Borramos clima y ponderaciones anteriores para regenerarlos desde HOY
        db.query(VariableMeteorologica).delete()
        db.query(DeporteSpot).delete()
        db.commit()

        hoy = datetime.utcnow().date()  # mismo criterio que usa la API (utcnow)
        filas = 0
        for spot in spots:
            for i in range(DIAS):
                fecha = hoy + timedelta(days=i)
                for nombre, (valor, prov) in _dia(spot, i).items():
                    db.add(VariableMeteorologica(
                        id_tipo_variable=tipos[nombre],
                        id_proveedor=provs[prov],
                        id_spot=spot.id,
                        fecha=fecha,
                        valor=str(valor),
                    ))
                    filas += 1
        db.commit()
        print(f"🌦️  Clima de muestra: {filas} filas ({len(spots)} spots x {DIAS} días).")

        ponderar_todos_los_deportes(db)  # lógica real del proyecto
    finally:
        db.close()


def generar_clima_spot(db, spot):
    """Clima de muestra para UN spot (lo usa el alta de spots en modo demo, en lugar
    de llamar a Google Weather / StormGlass). No toca los demas spots."""
    tipos = {t.nombre: t.id for t in db.query(TipoVariableMeteorologica).all()}
    provs = {p.nombre: p.id for p in db.query(ProveedorDatos).all()}
    db.query(VariableMeteorologica).filter(VariableMeteorologica.id_spot == spot.id).delete()
    hoy = datetime.utcnow().date()
    filas = 0
    for i in range(DIAS):
        fecha = hoy + timedelta(days=i)
        for nombre, (valor, prov) in _dia(spot, i).items():
            db.add(VariableMeteorologica(
                id_tipo_variable=tipos[nombre], id_proveedor=provs[prov],
                id_spot=spot.id, fecha=fecha, valor=str(valor),
            ))
            filas += 1
    db.commit()
    return filas


def main():
    if "--reset" in sys.argv:
        print("🧹 --reset: borrando todas las tablas...")
        Base.metadata.drop_all(bind=engine)
        import os, shutil
        from app.api.deporte_routes import ICON_DIR
        shutil.rmtree(ICON_DIR, ignore_errors=True)  # iconos de deportes subidos
    Base.metadata.create_all(bind=engine)
    cargar_base_si_esta_vacia()
    normalizar_coordenadas()
    refrescar_clima()
    print("✅ Datos demo listos.")


if __name__ == "__main__":
    main()
