import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL

# --- MODO DEMO -------------------------------------------------------------
# Si DATABASE_URL apunta a SQLite (ej: sqlite:///./nautic_demo.db) usamos un
# archivo local en BackEnd/ en vez de Postgres. Con Postgres todo funciona igual
# que antes.
_url = DATABASE_URL
_connect_args = {}
if _url and _url.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}
    if _url.startswith("sqlite:///./"):
        _backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        _file = os.path.join(_backend_dir, _url[len("sqlite:///./"):])
        _url = "sqlite:///" + _file.replace("\\", "/")

engine = create_engine(_url, connect_args=_connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal() #Crea una nueva sesión con la base de datos
    try:
        yield db #La “cede” temporalmente a FastAPI para usarla dentro del endpoint
    finally:
        db.close() #Cierra la sesión al finalizar la petición
