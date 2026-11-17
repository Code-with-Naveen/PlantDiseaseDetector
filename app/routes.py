"""Web pages and JSON API."""
import csv
import io
import json
from pathlib import Path

from flask import (Blueprint, Response, abort, current_app, jsonify, render_template, request,
                   send_from_directory)

from . import database as db
from .config import (MAX_BATCH_FILES, MAX_UPLOAD_MB, MODELS_DIR, SAMPLE_DIR,
                     UPLOAD_DIR)
from .knowledge import display_names, get_info
from .model import split_label
from .service import UserError, analyse, open_validated_image, remove_files

bp = Blueprint("main", __name__)


def _model():
    m = current_app.extensions.get("plant_model")
    if m is None:
        raise UserError(
            "The AI model is not loaded. Check that the 'models' folder contains "
            "plant_disease_resnet9.pth and class_names.json, then restart the app."
        )
    return m


def _read_json(name, default):
    p = MODELS_DIR / name
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


@bp.app_context_processor
def inject_globals():
    return {"model_ready": current_app.extensions.get("plant_model") is not None,
            "max_upload_mb": MAX_UPLOAD_MB, "max_batch": MAX_BATCH_FILES}


# ---------------------------------------------------------------- pages
@bp.route("/")
def index():
    return render_template("index.html", page="detect")


@bp.route("/batch")
def batch_page():
    return render_template("batch.html", page="batch")


@bp.route("/history")
def history_page():
    return render_template("history.html", page="history", plants=db.distinct_plants())


@bp.route("/dashboard")
def dashboard_page():
    return render_template("dashboard.html", page="dashboard")


@bp.route("/model")
def model_page():
    meta = _read_json("model_meta.json", {})
    m = current_app.extensions.get("plant_model")
    if m is not None:
        meta = {**meta, **{k: v for k, v in m.meta.items() if k == "weights_source"}}
        meta["img_size"] = m.img_size
    return render_template("model.html", page="model", meta=meta,
                           history=_read_json("training_history.json", []),
                           classes=_read_json("class_metrics.json", []))


@bp.route("/about")
def about_page():
    names = _read_json("class_names.json", [])
    crops = {}
    for n in names:
        p, c = split_label(n)
        p, c = display_names(p, c)
        crops.setdefault(p, []).append(c)
    return render_template("about.html", page="about", crops=dict(sorted(crops.items())))


# ---------------------------------------------------------------- files
@bp.route("/uploads/<path:name>")
def uploads(name):
    return send_from_directory(UPLOAD_DIR, name)


@bp.route("/sample-image/<path:name>")
def sample_image(name):
    return send_from_directory(SAMPLE_DIR, name)


# ---------------------------------------------------------------- API
def _list_samples():
    out = []
    if SAMPLE_DIR.exists():
        for folder in sorted(p for p in SAMPLE_DIR.iterdir() if p.is_dir()):
            plant_raw, cond_raw = split_label(folder.name)
            plant, cond = display_names(plant_raw, cond_raw)
            for f in sorted(folder.glob("*.*")):
                out.append({"path": f"{folder.name}/{f.name}", "plant": plant, "condition": cond,
                            "healthy": cond_raw.lower() == "healthy"})
    return out


@bp.route("/api/samples")
def api_samples():
    return jsonify(_list_samples())


@bp.route("/api/predict", methods=["POST"])
def api_predict():
    f = request.files.get("image")
    if f is None or not f.filename:
        raise UserError("No image received. Choose a leaf photo first.")
    model = _model()
    img = open_validated_image(f.stream, f.filename)
    return jsonify(analyse(model, img, Path(f.filename).name))


@bp.route("/api/predict-sample", methods=["POST"])
def api_predict_sample():
    rel = (request.get_json(silent=True) or {}).get("path", "")
    target = (SAMPLE_DIR / rel).resolve()
    if SAMPLE_DIR.resolve() not in target.parents or not target.is_file():
        raise UserError("Sample image not found.")
    model = _model()
    with open(target, "rb") as fh:
        img = open_validated_image(fh, target.name)
    return jsonify(analyse(model, img, f"sample: {target.name}"))


@bp.route("/api/batch", methods=["POST"])
def api_batch():
    files = [f for f in request.files.getlist("images") if f.filename]
    if not files:
        raise UserError("No images received. Select one or more leaf photos.")
    if len(files) > MAX_BATCH_FILES:
        raise UserError(f"Too many files. Please upload at most {MAX_BATCH_FILES} at a time.")
    model = _model()
    results = []
    for f in files:
        try:
            img = open_validated_image(f.stream, f.filename)
            r = analyse(model, img, Path(f.filename).name)
            results.append({"ok": True, **r})
        except UserError as e:
            results.append({"ok": False, "filename": f.filename, "error": str(e)})
    return jsonify(results)


@bp.route("/api/history")
def api_history():
    rows = db.list_predictions(plant=request.args.get("plant") or None,
                               status=request.args.get("status") or None,
                               q=(request.args.get("q") or "").strip() or None)
    for r in rows:
        r["image_url"] = f"/uploads/{r['image_file']}"
        r["heatmap_url"] = f"/uploads/{r['heatmap_file']}" if r["heatmap_file"] else None
        info = get_info(r["class_name"], r["is_healthy"])
        r["about"], r["treatment"], r["prevention"] = info["about"], info["treatment"], info["prevention"]
    return jsonify(rows)


@bp.route("/api/history/<int:pid>", methods=["DELETE"])
def api_history_delete(pid):
    files = db.delete_prediction(pid)
    if files is None:
        return jsonify(error="Record not found."), 404
    remove_files(files)
    return jsonify(ok=True)


@bp.route("/api/history", methods=["DELETE"])
def api_history_clear():
    remove_files(db.clear_predictions())
    return jsonify(ok=True)


@bp.route("/api/history/export.csv")
def export_csv():
    rows = db.list_predictions(limit=100000)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["id", "date_time", "file", "plant", "condition", "healthy", "confidence_percent"])
    for r in rows:
        w.writerow([r["id"], r["created_at"], r["original_name"], r["plant"], r["condition"],
                    "yes" if r["is_healthy"] else "no", round(r["confidence"] * 100, 2)])
    return Response(buf.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=prediction_history.csv"})


@bp.route("/api/stats")
def api_stats():
    return jsonify(db.stats())


@bp.route("/api/health")
def api_health():
    m = current_app.extensions.get("plant_model")
    return jsonify(status="ok", model_loaded=m is not None,
                   classes=len(m.class_names) if m else 0)


# ---------------------------------------------------------------- errors
def _wants_json():
    return request.path.startswith("/api/")


@bp.app_errorhandler(UserError)
def handle_user_error(e):
    return jsonify(error=str(e)), 400


@bp.app_errorhandler(413)
def too_large(e):
    msg = f"File too large. Maximum upload size is {MAX_UPLOAD_MB} MB."
    if _wants_json():
        return jsonify(error=msg), 413
    return render_template("error.html", page="", code=413, message=msg), 413


@bp.app_errorhandler(404)
def not_found(e):
    if _wants_json():
        return jsonify(error="Not found."), 404
    return render_template("error.html", page="", code=404, message="Page not found."), 404


@bp.app_errorhandler(Exception)
def server_error(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    current_app.logger.exception("Unhandled error")
    msg = "Something went wrong while processing your request. Please try again."
    if _wants_json():
        return jsonify(error=msg), 500
    return render_template("error.html", page="", code=500, message=msg), 500
