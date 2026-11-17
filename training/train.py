"""Train / re-train the ResNet9 plant-disease classifier.

Recipe follows the original notebook: ResNet9, Adam, One-Cycle LR schedule,
gradient clipping, weight decay.

Usage (from the project root, with the virtual environment active):

    python training/train.py --data path\\to\\dataset --epochs 8 --img-size 96

The dataset folder must contain one sub-folder per class, e.g.
    dataset/Tomato___Late_blight/img1.jpg
or the Kaggle layout with  train/  and  valid/  sub-folders.
Results are written to the  models/  folder and picked up by the app automatically.
"""
import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.model import ResNet9  # noqa: E402

IMG_EXT = {".jpg", ".jpeg", ".png", ".bmp"}


def load_folder(folder: Path, classes, img_size, max_per_class, seed):
    rng = random.Random(seed)
    X, y = [], []
    for ci, cname in enumerate(classes):
        files = sorted(p for p in (folder / cname).iterdir() if p.suffix.lower() in IMG_EXT)
        rng.shuffle(files)
        if max_per_class:
            files = files[:max_per_class]
        for p in files:
            with Image.open(p) as im:
                X.append(np.asarray(im.convert("RGB").resize((img_size, img_size), Image.BILINEAR)))
            y.append(ci)
    return np.stack(X), np.array(y)


def to_tensor(X):
    return torch.from_numpy(X).permute(0, 3, 1, 2).contiguous()  # uint8 NCHW


def augment(xb):
    """Light augmentation on a float batch in 0..1."""
    if random.random() < 0.5:
        xb = torch.flip(xb, dims=[3])
    if random.random() < 0.5:
        xb = torch.flip(xb, dims=[2])
    gain = 1.0 + (torch.rand(xb.size(0), 1, 1, 1) - 0.5) * 0.2
    return (xb * gain).clamp(0, 1)


@torch.no_grad()
def evaluate(model, X, y, bs=64):
    model.eval()
    preds, losses = [], []
    for i in range(0, len(X), bs):
        xb = X[i:i + bs].float() / 255.0
        out = model(xb)
        losses.append(F.cross_entropy(out, y[i:i + bs], reduction="sum").item())
        preds.append(out.argmax(1))
    preds = torch.cat(preds)
    return sum(losses) / len(X), (preds == y).float().mean().item(), preds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="dataset folder (class sub-folders)")
    ap.add_argument("--img-size", type=int, default=96)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--lr", type=float, default=0.005)
    ap.add_argument("--max-per-class", type=int, default=150, help="0 = use all images")
    ap.add_argument("--val-per-class", type=int, default=25)
    ap.add_argument("--out", default=str(ROOT / "models"))
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    random.seed(args.seed)
    data = Path(args.data)
    if (data / "train").is_dir() and (data / "valid").is_dir():
        train_dir, valid_dir = data / "train", data / "valid"
    else:
        train_dir, valid_dir = data, None
    classes = sorted(p.name for p in train_dir.iterdir() if p.is_dir())
    print(f"Found {len(classes)} classes", flush=True)

    t0 = time.time()
    if valid_dir is not None:
        Xtr, ytr = load_folder(train_dir, classes, args.img_size, args.max_per_class, args.seed)
        Xva, yva = load_folder(valid_dir, classes, args.img_size, args.val_per_class, args.seed)
    else:
        X, y = load_folder(train_dir, classes, args.img_size, args.max_per_class + args.val_per_class, args.seed)
        va_idx = []
        for c in range(len(classes)):
            va_idx += list(np.where(y == c)[0][: args.val_per_class])
        mask = np.zeros(len(y), bool)
        mask[va_idx] = True
        Xtr, ytr, Xva, yva = X[~mask], y[~mask], X[mask], y[mask]
    print(f"Loaded {len(Xtr)} train / {len(Xva)} validation images in {time.time()-t0:.0f}s", flush=True)

    Xtr, Xva = to_tensor(Xtr), to_tensor(Xva)
    ytr, yva = torch.from_numpy(ytr).long(), torch.from_numpy(yva).long()

    model = ResNet9(3, len(classes))
    opt = torch.optim.Adam(model.parameters(), args.lr, weight_decay=1e-4)
    steps = (len(Xtr) + args.batch_size - 1) // args.batch_size
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, args.lr, epochs=args.epochs, steps_per_epoch=steps)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    history = []
    for epoch in range(args.epochs):
        model.train()
        perm = torch.randperm(len(Xtr))
        tl, tc, n = 0.0, 0, 0
        t_ep = time.time()
        for s in range(steps):
            idx = perm[s * args.batch_size:(s + 1) * args.batch_size]
            xb, yb = augment(Xtr[idx].float() / 255.0), ytr[idx]
            logits = model(xb)
            loss = F.cross_entropy(logits, yb)
            loss.backward()
            nn.utils.clip_grad_value_(model.parameters(), 0.1)
            opt.step()
            opt.zero_grad()
            sched.step()
            tl += loss.item() * len(idx)
            tc += (logits.argmax(1) == yb).sum().item()
            n += len(idx)
            if s % 20 == 0:
                print(f"  epoch {epoch+1}/{args.epochs} step {s}/{steps} loss {loss.item():.3f}", flush=True)
        vl, va, preds = evaluate(model, Xva, yva)
        rec = dict(epoch=epoch + 1, train_loss=tl / n, train_acc=tc / n, val_loss=vl, val_acc=va)
        history.append(rec)
        print(f"Epoch {epoch+1}/{args.epochs}: train_loss {rec['train_loss']:.4f} train_acc {rec['train_acc']:.4f} "
              f"val_loss {vl:.4f} val_acc {va:.4f}  ({time.time()-t_ep:.0f}s)", flush=True)

        # save after every epoch so an interrupted run still leaves a usable model
        torch.save(model.state_dict(), out / "plant_disease_resnet9.pth")
        (out / "class_names.json").write_text(json.dumps(classes, indent=1), encoding="utf-8")
        (out / "training_history.json").write_text(json.dumps(history, indent=1), encoding="utf-8")

    # per-class metrics
    per_class = []
    for ci, cname in enumerate(classes):
        m = yva == ci
        tp = int(((preds == ci) & m).sum())
        fp = int(((preds == ci) & ~m).sum())
        fn = int(((preds != ci) & m).sum())
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec_ = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec_ / (prec + rec_) if prec + rec_ else 0.0
        per_class.append(dict(name=cname, support=int(m.sum()), precision=prec, recall=rec_, f1=f1))
    (out / "class_metrics.json").write_text(json.dumps(per_class, indent=1), encoding="utf-8")

    meta = dict(
        architecture="ResNet9",
        img_size=args.img_size,
        num_classes=len(classes),
        epochs=args.epochs,
        batch_size=args.batch_size,
        max_lr=args.lr,
        optimizer="Adam + OneCycleLR, grad-clip 0.1, weight-decay 1e-4",
        n_train=len(Xtr),
        n_val=len(Xva),
        val_accuracy=history[-1]["val_acc"],
        dataset="PlantVillage (raw/color subset)",
        trained_on=time.strftime("%Y-%m-%d"),
        parameters=int(sum(p.numel() for p in model.parameters())),
    )
    (out / "model_meta.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print(f"Done. Final validation accuracy: {history[-1]['val_acc']*100:.2f}%  Total time {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
