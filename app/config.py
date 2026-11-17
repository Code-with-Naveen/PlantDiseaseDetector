"""Central configuration. Nothing here needs to be edited to run the app."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
INSTANCE_DIR = Path(os.environ.get("PDD_INSTANCE_DIR", BASE_DIR / "instance"))
UPLOAD_DIR = INSTANCE_DIR / "uploads"
DB_PATH = INSTANCE_DIR / "plant_disease.db"
MODELS_DIR = BASE_DIR / "models"
SAMPLE_DIR = BASE_DIR / "sample_images"

MAX_UPLOAD_MB = 10
MAX_BATCH_FILES = 20
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
MIN_IMAGE_SIDE = 48          # reject images smaller than this (pixels)
STORED_MAX_SIDE = 1024       # uploads are downscaled to this before saving
LOW_CONFIDENCE = 0.60        # below this the UI warns that the result is uncertain

DEFAULT_PORT = int(os.environ.get("PORT", "5000"))
