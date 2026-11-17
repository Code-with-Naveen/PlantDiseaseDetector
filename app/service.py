"""Glue between uploaded images, the model, the knowledge base and the database."""
import threading
import uuid
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from . import database as db
from .config import (ALLOWED_EXTENSIONS, LOW_CONFIDENCE, MIN_IMAGE_SIDE, STORED_MAX_SIDE,
                     UPLOAD_DIR)
from .knowledge import display_names, get_info
from .model import PlantDiseaseModel, overlay_heatmap, split_label

_infer_lock = threading.Lock()   # the model is shared; run one inference at a time


class UserError(Exception):
    """A problem with the user's input that should be shown nicely in the UI."""


def open_validated_image(file_storage_or_path, filename: str) -> Image.Image:
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise UserError(f"Unsupported file type '{ext or 'unknown'}'. "
                        f"Please upload a JPG, PNG, BMP or WEBP image.")
    try:
        img = Image.open(file_storage_or_path)
        img.verify()                       # detects truncated / corrupt files
        if hasattr(file_storage_or_path, "seek"):
            file_storage_or_path.seek(0)
        img = Image.open(file_storage_or_path)
        img = ImageOps.exif_transpose(img).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError):
        raise UserError("This file could not be read as an image. It may be corrupted.")
    if min(img.size) < MIN_IMAGE_SIDE:
        raise UserError(f"Image is too small ({img.width}x{img.height}px). "
                        f"Use a photo at least {MIN_IMAGE_SIDE}px on each side.")
    img.thumbnail((STORED_MAX_SIDE, STORED_MAX_SIDE))
    return img


def analyse(model: PlantDiseaseModel, img: Image.Image, original_name: str) -> dict:
    """Run the model on a validated image, store everything, return a JSON-able dict."""
    with _infer_lock:
        top = model.predict(img, top_k=5)
        cam = model.gradcam(img, class_index=model.class_names.index(top[0][0]))

    class_name, confidence = top[0]
    plant_raw, cond_raw = split_label(class_name)
    healthy = cond_raw.lower() == "healthy"
    plant, condition = display_names(plant_raw, cond_raw)

    token = uuid.uuid4().hex
    image_file, heat_file = f"{token}.jpg", f"{token}_cam.jpg"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    img.save(UPLOAD_DIR / image_file, "JPEG", quality=90)
    overlay_heatmap(img, cam).save(UPLOAD_DIR / heat_file, "JPEG", quality=90)

    top5 = []
    for cname, conf in top:
        p_raw, c_raw = split_label(cname)
        p, c = display_names(p_raw, c_raw)
        top5.append({"label": f"{p} - {c}", "confidence": round(conf, 4), "healthy": c_raw.lower() == "healthy"})

    pid = db.add_prediction(original_name, image_file, heat_file, class_name, plant, condition,
                            healthy, confidence, top5)
    info = get_info(class_name, healthy)
    return {
        "id": pid,
        "plant": plant,
        "condition": condition,
        "healthy": healthy,
        "confidence": round(confidence, 4),
        "low_confidence": confidence < LOW_CONFIDENCE,
        "top5": top5,
        "about": info["about"],
        "treatment": info["treatment"],
        "prevention": info["prevention"],
        "image_url": f"/uploads/{image_file}",
        "heatmap_url": f"/uploads/{heat_file}",
        "filename": original_name,
    }


def remove_files(names):
    for n in names or []:
        try:
            (UPLOAD_DIR / n).unlink(missing_ok=True)
        except OSError:
            pass
