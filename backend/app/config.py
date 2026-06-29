"""Application configuration constants."""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

# App
APP_NAME = os.getenv("APP_NAME", "BhaktiAstro")
APP_ENV = os.getenv("APP_ENV", "development")
APP_DEBUG = os.getenv("APP_DEBUG", "true").lower() == "true"
APP_VERSION = os.getenv("APP_VERSION", "0.1.0")

# Language
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "hi")
SUPPORTED_LANGUAGES = ["hi", "en"]

# Ayanamsa
AYANAMSA_DEFAULT = os.getenv("DEFAULT_AYANAMSA", "lahiri")
AYANAMSA_OPTIONS = ["lahiri", "raman", "kp"]

# Timezone
DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "Asia/Kolkata")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bhaktiastro.db")

# Swiss Ephemeris path
EPHE_PATH = os.getenv("EPHE_PATH", str(BASE_DIR / "data" / "ephe"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Tolerances
TOLERANCE_SUNRISE_MINUTES = 2
TOLERANCE_TITHI_MINUTES = 5
TOLERANCE_NAKSHATRA_MINUTES = 5
TOLERANCE_LAGNA_DEGREES = 0.25
