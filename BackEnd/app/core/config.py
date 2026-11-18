from dotenv import load_dotenv
import os

load_dotenv()

# MODO DEMO: si no hay DATABASE_URL (ni en el entorno ni en un .env) se usa una base SQLite
# local en BackEnd/nautic_demo.db. Para volver a Postgres, definí DATABASE_URL en un .env.
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./nautic_demo.db"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY")
