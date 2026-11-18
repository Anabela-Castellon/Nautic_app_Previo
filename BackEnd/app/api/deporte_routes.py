import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Deporte

router = APIRouter(prefix="/deporte", tags=["Deporte"])

# Carpeta donde se guardan los iconos PNG que el admin sube para cada deporte
# (BackEnd/sport_icons/<id>.png). No requiere cambios en la base de datos.
ICON_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "sport_icons"))
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_ICON_BYTES = 2 * 1024 * 1024


def icon_path(deporte_id: int) -> str:
    return os.path.join(ICON_DIR, f"{int(deporte_id)}.png")


def save_icon(deporte_id: int, data: bytes) -> None:
    if not data.startswith(PNG_SIGNATURE):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen PNG.")
    if len(data) > MAX_ICON_BYTES:
        raise HTTPException(status_code=400, detail="La imagen no puede superar 2 MB.")
    os.makedirs(ICON_DIR, exist_ok=True)
    with open(icon_path(deporte_id), "wb") as f:
        f.write(data)


@router.get("/list")
def get_deportes(db: Session = Depends(get_db)):
    deportes = db.query(Deporte).filter(Deporte.activo == True).all()
    result = []
    for d in deportes:
        path = icon_path(d.id)
        icono_url = f"/deporte/icono/{d.id}?v={int(os.path.getmtime(path))}" if os.path.exists(path) else None
        result.append({
            "id": d.id,
            "nombre": d.nombre,
            "codigo": d.codigo,
            "descripcion": d.descripcion,
            "icono_url": icono_url,
        })
    return result


@router.get("/icono/{deporte_id}")
def get_icono(deporte_id: int):
    path = icon_path(deporte_id)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Este deporte no tiene icono")
    with open(path, "rb") as f:
        return Response(content=f.read(), media_type="image/png")
