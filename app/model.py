"""ResNet9 architecture (same as the training notebook) + inference helpers."""
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image


def conv_block(in_ch, out_ch, pool=False):
    layers = [
        nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
        nn.BatchNorm2d(out_ch),
        nn.ReLU(inplace=True),
    ]
    if pool:
        layers.append(nn.MaxPool2d(4))
    return nn.Sequential(*layers)


class ResNet9(nn.Module):
    """Same layer layout as the notebook, so notebook weights load directly.

    The only change: the final pooling is adaptive, so any input size that is a
    multiple of 64 (64, 128, 192, 256 ...) works with the same weights.
    """

    def __init__(self, in_channels, num_classes):
        super().__init__()
        self.conv1 = conv_block(in_channels, 64)
        self.conv2 = conv_block(64, 128, pool=True)
        self.res1 = nn.Sequential(conv_block(128, 128), conv_block(128, 128))
        self.conv3 = conv_block(128, 256, pool=True)
        self.conv4 = conv_block(256, 512, pool=True)
        self.res2 = nn.Sequential(conv_block(512, 512), conv_block(512, 512))
        self.classifier = nn.Sequential(
            nn.AdaptiveMaxPool2d(1), nn.Flatten(), nn.Linear(512, num_classes)
        )

    def features(self, x):
        out = self.conv1(x)
        out = self.conv2(out)
        out = self.res1(out) + out
        out = self.conv3(out)
        out = self.conv4(out)
        out = self.res2(out) + out
        return out

    def forward(self, x):
        return self.classifier(self.features(x))


def split_label(class_name: str):
    """'Tomato___Late_blight' -> ('Tomato', 'Late blight')."""
    plant, _, cond = class_name.partition("___")
    plant = plant.replace("_", " ").replace("(including sour)", "").replace(",", "")
    plant = " ".join(plant.split())
    cond = " ".join(cond.replace("_", " ").split()) or "unknown"
    return plant, cond


class PlantDiseaseModel:
    def __init__(self, models_dir: Path):
        self.models_dir = Path(models_dir)
        self.device = torch.device("cpu")
        self.class_names = json.loads(
            (self.models_dir / "class_names.json").read_text(encoding="utf-8")
        )
        meta_path = self.models_dir / "model_meta.json"
        self.meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        self.img_size = int(self.meta.get("img_size", 128))

        # If the notebook's own weights are dropped into models/, use them (256px).
        notebook_weights = self.models_dir / "plant-disease-model.pth"
        weights = self.models_dir / "plant_disease_resnet9.pth"
        if notebook_weights.exists():
            weights = notebook_weights
            self.img_size = 256
            self.meta["weights_source"] = "plant-disease-model.pth (notebook weights, 256 px)"
        if not weights.exists():
            raise FileNotFoundError(f"Model weights not found: {weights}")

        self.model = ResNet9(3, len(self.class_names))
        state = torch.load(weights, map_location=self.device, weights_only=True)
        self.model.load_state_dict(state)
        self.model.eval()
        self.weights_file = weights.name

    # ---- preprocessing -------------------------------------------------
    def preprocess(self, img: Image.Image) -> torch.Tensor:
        img = img.convert("RGB").resize((self.img_size, self.img_size), Image.BILINEAR)
        arr = np.asarray(img, dtype=np.float32) / 255.0  # same scaling as the notebook
        return torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)

    # ---- prediction ----------------------------------------------------
    @torch.no_grad()
    def predict(self, img: Image.Image, top_k: int = 5):
        x = self.preprocess(img)
        probs = F.softmax(self.model(x), dim=1)[0]
        conf, idx = torch.topk(probs, k=min(top_k, len(self.class_names)))
        return [(self.class_names[i], float(c)) for c, i in zip(conf.tolist(), idx.tolist())]

    # ---- Grad-CAM ------------------------------------------------------
    def gradcam(self, img: Image.Image, class_index=None):
        """Return a heatmap (H x W, values 0..1) showing where the model looked.

        Uses the conv3 feature map (finer resolution than the final layer).
        """
        m = self.model
        x = self.preprocess(img)
        with torch.enable_grad():
            out = m.conv2(m.conv1(x))
            out = m.res1(out) + out
            mid = m.conv3(out)
            mid.retain_grad()
            out = m.conv4(mid)
            out = m.res2(out) + out
            logits = m.classifier(out)
            if class_index is None:
                class_index = int(logits.argmax(dim=1))
            m.zero_grad()
            logits[0, class_index].backward()
            weights = mid.grad.mean(dim=(2, 3), keepdim=True)
            cam = F.relu((weights * mid).sum(dim=1, keepdim=True))
            cam = F.interpolate(
                cam, size=(self.img_size, self.img_size), mode="bilinear", align_corners=False
            )
        cam = cam[0, 0].detach().numpy()
        cam = cam - cam.min()
        if cam.max() > 0:
            cam = cam / cam.max()
        return cam


def overlay_heatmap(img: Image.Image, cam: np.ndarray, alpha: float = 0.45) -> Image.Image:
    """Blend a jet-style heatmap over the image (pure numpy, no matplotlib)."""
    base = img.convert("RGB").resize((cam.shape[1], cam.shape[0]), Image.BILINEAR)
    c = np.clip(cam, 0, 1)
    r = np.clip(1.5 - np.abs(4 * c - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * c - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * c - 1), 0, 1)
    heat = np.stack([r, g, b], axis=-1) * 255
    blended = (1 - alpha) * np.asarray(base, dtype=np.float32) + alpha * heat
    return Image.fromarray(blended.clip(0, 255).astype(np.uint8))
