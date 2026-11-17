r"""End-to-end smoke test (uses a temporary database, your real history is untouched).

Run:  .venv\Scripts\python tests\smoke_test.py
"""
import io
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ["PDD_INSTANCE_DIR"] = tempfile.mkdtemp(prefix="pdd_test_")
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402

from app import create_app  # noqa: E402

app = create_app()
c = app.test_client()
passed = failed = 0


def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name} {extra}")


print("Pages")
for url in ["/", "/batch", "/history", "/dashboard", "/model", "/about", "/api/health", "/api/samples"]:
    r = c.get(url)
    check(f"GET {url} -> 200", r.status_code == 200, r.status_code)
check("model loaded", c.get("/api/health").json["model_loaded"])
check("404 page", c.get("/nope").status_code == 404)

print("Sample-based prediction accuracy")
samples = sorted((ROOT / "sample_images").glob("*/*.*"))
correct = 0
for s in samples:
    rel = f"{s.parent.name}/{s.name}"
    r = c.post("/api/predict-sample", json={"path": rel})
    if r.status_code == 200:
        j = r.json
        from app.model import split_label
        from app.knowledge import display_names
        truth = display_names(*split_label(s.parent.name))
        correct += (j["plant"], j["condition"]) == truth
check(f"predicted {len(samples)} bundled samples", len(samples) > 0)
acc = correct / max(1, len(samples))
print(f"  INFO  accuracy on unseen bundled samples: {correct}/{len(samples)} = {acc:.1%}")
check("sample accuracy >= 80%", acc >= 0.80)

print("Upload + validation")
buf = io.BytesIO(); Image.open(samples[0]).save(buf, "PNG"); buf.seek(0)
r = c.post("/api/predict", data={"image": (buf, "leaf.png")}, content_type="multipart/form-data")
check("valid upload -> 200", r.status_code == 200, r.get_data(as_text=True)[:200])
j = r.json
check("response has result fields", all(k in j for k in ["plant", "condition", "confidence", "top5", "treatment", "heatmap_url"]))
check("uploaded + heatmap files served", c.get(j["image_url"]).status_code == 200 and c.get(j["heatmap_url"]).status_code == 200)

r = c.post("/api/predict", data={}, content_type="multipart/form-data")
check("no file -> 400 with message", r.status_code == 400 and "error" in r.json)
r = c.post("/api/predict", data={"image": (io.BytesIO(b"not an image"), "x.jpg")}, content_type="multipart/form-data")
check("corrupt image -> 400", r.status_code == 400 and "could not be read" in r.json["error"])
r = c.post("/api/predict", data={"image": (io.BytesIO(b"hello"), "x.txt")}, content_type="multipart/form-data")
check("wrong extension -> 400", r.status_code == 400 and "Unsupported" in r.json["error"])
tiny = io.BytesIO(); Image.new("RGB", (10, 10)).save(tiny, "PNG"); tiny.seek(0)
r = c.post("/api/predict", data={"image": (tiny, "tiny.png")}, content_type="multipart/form-data")
check("tiny image -> 400", r.status_code == 400 and "too small" in r.json["error"])
r = c.post("/api/predict-sample", json={"path": "../../etc/passwd"})
check("path traversal blocked", r.status_code == 400)

print("Batch")
files = []
for s in samples[:3]:
    b = io.BytesIO(s.read_bytes()); files.append((b, s.name))
files.append((io.BytesIO(b"junk"), "bad.jpg"))
r = c.post("/api/batch", data={"images": files}, content_type="multipart/form-data")
res = r.json
check("batch -> 4 results", r.status_code == 200 and len(res) == 4)
check("batch: 3 ok, 1 failed", sum(x["ok"] for x in res) == 3 and not res[3]["ok"])

print("History / stats / export / delete")
h = c.get("/api/history").json
check("history has 5 records (1 upload + 3 batch + samples)", len(h) >= 5, len(h))
check("history filter works", all(not x["is_healthy"] for x in c.get("/api/history?status=diseased").json))
check("search works", isinstance(c.get("/api/history?q=tomato").json, list))
st = c.get("/api/stats").json
check("stats consistent", st["total"] == st["healthy"] + st["diseased"] and st["total"] == len(h))
csv_r = c.get("/api/history/export.csv")
check("CSV export", csv_r.status_code == 200 and csv_r.get_data(as_text=True).startswith("id,"))
rid = h[0]["id"]
check("delete record", c.delete(f"/api/history/{rid}").status_code == 200)
check("delete missing -> 404", c.delete("/api/history/999999").status_code == 404)
check("clear history", c.delete("/api/history").status_code == 200 and c.get("/api/history").json == [])

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
