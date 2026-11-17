# 🌿 Plant Disease Detector

An AI application that looks at a photo of a plant leaf and tells you **which crop it is, whether it is healthy or
diseased, which disease it is**, and what to do about it. It runs entirely on your own Windows computer – no cloud, no
API keys, no accounts, and your images never leave your machine.

**Based on your notebook:** the model is the same **ResNet9** (PyTorch) architecture from
*plant-disease-classification-resnet-99-2.ipynb*, trained on the **PlantVillage** dataset (38 classes: 14 crops, 26 diseases).

---

## 🚀 Quick start (3 steps)

1. **Extract** the ZIP file (right-click → *Extract All…*). Do not run it from inside the ZIP.
2. **Double-click `run.bat`.**
3. Wait. The first run installs everything automatically (about 3–8 minutes, **internet required once**).
   Your web browser then opens the app by itself at `http://127.0.0.1:5000`.

From the second run onwards it starts in a few seconds and works **offline**.

**Requirement:** Python **3.9 – 3.13** (3.12 recommended). If it is missing, `run.bat` tells you and opens the download
page – install it, tick **“Add python.exe to PATH”**, then double-click `run.bat` again.

> To stop the app, close the black console window (or press `Ctrl+C` in it).

---

## ✨ Features

| Page | What it does |
|------|--------------|
| **Detect** | Drag & drop (or browse) a leaf photo → crop, disease, confidence, top-5 predictions, a **Grad-CAM heatmap** of where the AI looked, plus description, treatment and prevention advice. |
| **Try a sample** | 152 ready-made leaf photos (4 per class) are included. Click one to test instantly – no photo needed. |
| **Batch** | Analyse up to 20 photos at once and see a results table. |
| **History** | Every analysis is saved in a local SQLite database. Search, filter, view details, delete, or **export to CSV**. |
| **Dashboard** | Charts: healthy vs diseased, analyses per plant, most detected diseases, activity over time. |
| **Model** | Accuracy, training curves and per-class performance. |
| **About** | How it works, supported crops/diseases, tips and limitations. |

Built-in validation and error handling: wrong file types, corrupt or tiny images, oversized uploads, empty submissions,
path-traversal attempts, a missing model file – each gives a clear message instead of crashing. Low-confidence results
are flagged with a warning.

---

## 📁 Project structure

```
PlantDiseaseDetector/
├── run.bat                  ← double-click this
├── main.py                  ← starts the server and opens the browser
├── requirements.txt         ← Python dependencies
├── README.md
├── app/
│   ├── __init__.py          ← app factory: creates DB, loads model
│   ├── config.py            ← settings (nothing to edit)
│   ├── model.py             ← ResNet9 + prediction + Grad-CAM
│   ├── service.py           ← validation, image storage, inference pipeline
│   ├── routes.py            ← web pages + JSON API + error handlers
│   ├── database.py          ← SQLite layer
│   ├── knowledge.py         ← disease descriptions / treatment / prevention
│   ├── templates/           ← HTML pages (Jinja)
│   └── static/              ← CSS, JavaScript, Chart.js (bundled, works offline)
├── models/
│   ├── plant_disease_resnet9.pth   ← trained weights
│   ├── class_names.json            ← the 38 class names
│   ├── model_meta.json             ← training details
│   ├── training_history.json       ← per-epoch loss / accuracy
│   └── class_metrics.json          ← per-class precision / recall / F1
├── sample_images/           ← 152 test leaf photos (4 per class, not used in training)
├── training/train.py        ← optional: re-train the model
├── tests/smoke_test.py      ← optional: automated end-to-end test
└── instance/                ← created automatically: database + uploaded images
```

---

## 🧪 How well does it work?

| Measure | Result |
|---|---|
| Validation accuracy (950 unseen images, 25 per class) | **92.2%** |
| Accuracy on the 152 bundled sample images (`tests/smoke_test.py`) | **90.1%** (137 / 152) |
| Your notebook (full dataset, GPU, 256 px) | ~99% |

The bundled model was trained on a **small subset** (120 images per class, 96 px, 5 epochs, CPU only), so it is
noticeably less accurate than your notebook's model. Weakest classes:

  - Tomato - Early blight: 64% recall
  - Tomato - Target Spot: 76% recall
  - Apple - Apple scab: 80% recall
  - Tomato - Late blight: 80% recall

Results on photos taken outside the lab-style PlantVillage setting (busy backgrounds, field photos) will be lower still.
Use the options below to get closer to the notebook's accuracy.

---

## 🔁 Optional: train a more accurate model

The bundled model was trained on a **small subset** of PlantVillage at low resolution so that it could be produced on an
ordinary CPU. Your notebook reached ≈ 99 % by training on the full dataset on a GPU. You have two easy ways to get there:

### Option A – use the weights from your notebook (easiest)
At the end of your notebook the model is saved as `plant-disease-model.pth`. Download it from Kaggle and copy it into the
project's **`models`** folder, then restart the app. The app detects it automatically and switches to the 256 px
setting used in the notebook. (The class order is the same – alphabetical – as in the notebook.)

### Option B – re-train here
1. Get the dataset – either download *“New Plant Diseases Dataset (Augmented)”* from Kaggle, or fetch the original
   PlantVillage colour images (needs [Git](https://git-scm.com/)):
   ```
   git clone --depth 1 --filter=blob:none --sparse https://github.com/spMohanty/PlantVillage-Dataset
   cd PlantVillage-Dataset
   git sparse-checkout set --no-cone /raw/color/
   ```
2. Open a Command Prompt in the project folder and run:
   ```
   .venv\Scripts\python training\train.py --data path\to\PlantVillage-Dataset\raw\color --img-size 128 --epochs 8 --max-per-class 400
   ```
   (Works with the Kaggle layout too: point `--data` at the folder that contains `train` and `valid`.)
   Use `--max-per-class 0` for all images. Training on a CPU is slow – more images/epochs means more hours.
3. Restart the app. The new weights and charts are picked up automatically.

---

## 🛠 Troubleshooting

| Problem | Fix |
|---------|-----|
| “Python 3.9 – 3.13 was not found” | Install Python 3.12 from python.org and tick *Add python.exe to PATH*. Python 3.14 is not supported yet by PyTorch. |
| Package installation fails | Check your internet connection and run `run.bat` again – it resumes. If it keeps failing, delete the `.venv` folder and retry. |
| Browser did not open | Open the address printed in the console window (normally `http://127.0.0.1:5000`). |
| Port already in use | Nothing to do – the app automatically picks the next free port and prints it. |
| Windows SmartScreen warning | Click *More info → Run anyway* (the script is plain text you can open in Notepad). |
| Wrong result on a non-leaf photo | The model only knows the 38 listed classes and can be over-confident on other images; see **About**. |
| Start completely fresh | Delete the `.venv` folder (re-installs packages) and/or the `instance` folder (clears history). |

Run the automated test (optional): `.venv\Scripts\python tests\smoke_test.py`

---

## ⚠️ Disclaimer

This tool is a decision aid, not a laboratory diagnosis. Treatment suggestions are general guidance; for serious or fast-spreading
problems consult a local agricultural extension service.

## 🙏 Credits

* Dataset: **PlantVillage** – Hughes & Salathé (2015), <https://github.com/spMohanty/PlantVillage-Dataset>.
  Please check the dataset's own terms before redistributing the images.
* Model and training approach: ResNet9 with One-Cycle LR, gradient clipping and weight decay, from your notebook.
* Built with Flask, Waitress, PyTorch, Pillow, NumPy and Chart.js (MIT).
