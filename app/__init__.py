"""Plant Disease Detector - Flask application factory."""
import logging
import os

from flask import Flask

from . import database
from .config import MAX_UPLOAD_MB, MODELS_DIR, UPLOAD_DIR

log = logging.getLogger("plantdisease")


def create_app():
    app = Flask(__name__)
    # Request ceiling; large enough for a batch of images. Single uploads are checked in routes.
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_MB * 20 * 1024 * 1024

    # --- initial setup: folders + database -------------------------------
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    database.init_db()

    # --- model loading ---------------------------------------------------
    try:
        import torch
        from .model import PlantDiseaseModel
        torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))
        m = PlantDiseaseModel(MODELS_DIR)
        app.extensions["plant_model"] = m
        log.warning("Model loaded: %s | %d classes | input %dpx", m.weights_file,
                    len(m.class_names), m.img_size)
    except Exception as exc:  # the app still starts and explains the problem in the UI
        log.error("Could not load the model: %s", exc)

    from .routes import bp
    app.register_blueprint(bp)
    return app
