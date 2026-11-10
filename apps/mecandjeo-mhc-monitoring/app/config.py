import os

from dotenv import load_dotenv


# Load environment variables from a local .env file when present.
load_dotenv()

# Core application identity and runtime settings.
APP_ENV = os.getenv("APP_ENV", "dev")
APP_PROJECT_NAME = os.getenv("APP_PROJECT_NAME", "mecandjeo-mhc-monitoring")
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

# Database and JWT settings used by the API service.
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))
AUTO_CREATE_SCHEMA = os.getenv("AUTO_CREATE_SCHEMA", "false").lower() == "true"

# Phase 9: first-run bootstrap settings; leave blank outside local development.
BOOTSTRAP_ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL")
BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
SEED_SAMPLE_DATA = os.getenv("SEED_SAMPLE_DATA", "false").lower() == "true"


# Phase 11: run the idempotent bootstrap (reference data, admin, sample cranes) when the API starts.
# Defaults to the AUTO_CREATE_SCHEMA value so earlier local setups keep working unchanged.
RUN_BOOTSTRAP = os.getenv("RUN_BOOTSTRAP", os.getenv("AUTO_CREATE_SCHEMA", "false")).lower() == "true"