"""SQLite storage for prediction history (standard-library sqlite3, no setup needed)."""
import json
import sqlite3
from contextlib import contextmanager

from .config import DB_PATH, INSTANCE_DIR

SCHEMA = """
CREATE TABLE IF NOT EXISTS predictions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    original_name TEXT    NOT NULL,
    image_file    TEXT    NOT NULL,
    heatmap_file  TEXT,
    class_name    TEXT    NOT NULL,
    plant         TEXT    NOT NULL,
    condition     TEXT    NOT NULL,
    is_healthy    INTEGER NOT NULL,
    confidence    REAL    NOT NULL,
    top5_json     TEXT    NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pred_created ON predictions(created_at);
CREATE INDEX IF NOT EXISTS idx_pred_plant   ON predictions(plant);
"""


@contextmanager
def connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(SCHEMA)


def add_prediction(original_name, image_file, heatmap_file, class_name, plant, condition,
                   is_healthy, confidence, top5):
    with connect() as conn:
        cur = conn.execute(
            """INSERT INTO predictions
               (original_name, image_file, heatmap_file, class_name, plant, condition,
                is_healthy, confidence, top5_json)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (original_name, image_file, heatmap_file, class_name, plant, condition,
             int(is_healthy), float(confidence), json.dumps(top5)),
        )
        return cur.lastrowid


def _row(r):
    d = dict(r)
    d["is_healthy"] = bool(d["is_healthy"])
    d["top5"] = json.loads(d.pop("top5_json"))
    return d


def list_predictions(plant=None, status=None, q=None, limit=500):
    sql, args = "SELECT * FROM predictions WHERE 1=1", []
    if plant:
        sql += " AND plant = ?"
        args.append(plant)
    if status == "healthy":
        sql += " AND is_healthy = 1"
    elif status == "diseased":
        sql += " AND is_healthy = 0"
    if q:
        sql += " AND (original_name LIKE ? OR condition LIKE ? OR plant LIKE ?)"
        args += [f"%{q}%"] * 3
    sql += " ORDER BY id DESC LIMIT ?"
    args.append(limit)
    with connect() as conn:
        return [_row(r) for r in conn.execute(sql, args)]


def get_prediction(pid):
    with connect() as conn:
        r = conn.execute("SELECT * FROM predictions WHERE id = ?", (pid,)).fetchone()
        return _row(r) if r else None


def delete_prediction(pid):
    """Delete one row; returns the file names that should be removed from disk."""
    with connect() as conn:
        r = conn.execute("SELECT image_file, heatmap_file FROM predictions WHERE id=?", (pid,)).fetchone()
        if not r:
            return None
        conn.execute("DELETE FROM predictions WHERE id = ?", (pid,))
        return [f for f in (r["image_file"], r["heatmap_file"]) if f]


def clear_predictions():
    with connect() as conn:
        rows = conn.execute("SELECT image_file, heatmap_file FROM predictions").fetchall()
        conn.execute("DELETE FROM predictions")
    return [f for r in rows for f in (r["image_file"], r["heatmap_file"]) if f]


def distinct_plants():
    with connect() as conn:
        return [r[0] for r in conn.execute("SELECT DISTINCT plant FROM predictions ORDER BY plant")]


def stats():
    with connect() as conn:
        total = conn.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]
        healthy = conn.execute("SELECT COUNT(*) FROM predictions WHERE is_healthy=1").fetchone()[0]
        avg_conf = conn.execute("SELECT AVG(confidence) FROM predictions").fetchone()[0] or 0
        by_plant = [dict(r) for r in conn.execute(
            "SELECT plant, COUNT(*) AS n FROM predictions GROUP BY plant ORDER BY n DESC")]
        top_diseases = [dict(r) for r in conn.execute(
            """SELECT plant || ' - ' || condition AS label, COUNT(*) AS n FROM predictions
               WHERE is_healthy=0 GROUP BY plant, condition ORDER BY n DESC LIMIT 8""")]
        per_day = [dict(r) for r in conn.execute(
            """SELECT date(created_at) AS day, COUNT(*) AS n,
                      SUM(CASE WHEN is_healthy=0 THEN 1 ELSE 0 END) AS diseased
               FROM predictions GROUP BY day ORDER BY day DESC LIMIT 14""")][::-1]
        recent = [_row(r) for r in conn.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 5")]
    return dict(total=total, healthy=healthy, diseased=total - healthy, avg_confidence=avg_conf,
                by_plant=by_plant, top_diseases=top_diseases, per_day=per_day, recent=recent)
