from __future__ import annotations
import json, argparse, os
from dataclasses import dataclass
from typing import Tuple, List
import numpy as np

try:
    from sklearn.isotonic import IsotonicRegression
except Exception:
    IsotonicRegression = None

# ---- metrics ----
def brier_score(conf: np.ndarray, y: np.ndarray) -> float:
    return float(np.mean((conf - y) ** 2))

def ece_mce(conf: np.ndarray, y: np.ndarray, bins: int = 15) -> Tuple[float, float]:
    """Expected / Max Calibration Error."""
    assert conf.shape == y.shape
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece, mce = 0.0, 0.0
    n = len(conf)
    for i in range(bins):
        lo, hi = edges[i], edges[i+1]
        mask = (conf >= lo) & (conf < hi) if i < bins - 1 else (conf >= lo) & (conf <= hi)
        if not np.any(mask):
            continue
        acc = np.mean(y[mask])
        conf_avg = np.mean(conf[mask])
        gap = abs(acc - conf_avg)
        ece += (np.sum(mask) / n) * gap
        mce = max(mce, gap)
    return float(ece), float(mce)

# ---- calibrators ----
@dataclass
class TemperatureScaler:
    T: float = 1.0

    def fit(self, logit: np.ndarray, y: np.ndarray, lr: float = 0.1, steps: int = 200) -> "TemperatureScaler":
        """Simple 1D SGD on NLL for binary logits (pre-sigmoid)."""
        eps = 1e-12
        T = 1.0
        for _ in range(steps):
            p = 1/(1+np.exp(-(logit/T)))
            grad = np.mean((p - y) * (logit / (T**2 + eps)))
            T -= lr * grad
            T = max(0.05, min(T, 50.0))
        self.T = float(T)
        return self

    def transform(self, logit: np.ndarray) -> np.ndarray:
        return 1/(1+np.exp(-(logit/self.T)))

class IsotonicCalibrator:
    def __init__(self):
        if IsotonicRegression is None:
            raise ImportError("scikit-learn is required for IsotonicCalibrator")
        self.iso = IsotonicRegression(out_of_bounds="clip")

    def fit(self, conf: np.ndarray, y: np.ndarray) -> "IsotonicCalibrator":
        self.iso.fit(conf, y)
        return self

    def transform(self, conf: np.ndarray) -> np.ndarray:
        return self.iso.transform(conf)

# ---- auto selector ----
def auto_calibrate(conf: np.ndarray, y: np.ndarray, logits: np.ndarray | None = None, seed: int = 42):
    """Splits into train/val; returns best of Temperature / Isotonic by ECE."""
    rng = np.random.default_rng(seed)
    idx = rng.permutation(len(conf))
    k = max(10, int(0.8 * len(conf)))
    tr, va = idx[:k], idx[k:]

    results = []

    # Isotonic on confidences
    if IsotonicRegression is not None:
        iso = IsotonicCalibrator().fit(conf[tr], y[tr])
        c_val = iso.transform(conf[va])
        ece, mce = ece_mce(c_val, y[va])
        results.append(("isotonic", {"ece": ece, "mce": mce, "cal": iso}))

    # Temperature scaling on logits (if provided)
    if logits is not None:
        ts = TemperatureScaler().fit(logits[tr], y[tr])
        c_val = ts.transform(logits[va])
        ece, mce = ece_mce(c_val, y[va])
        results.append(("temperature", {"ece": ece, "mce": mce, "cal": ts}))

    if not results:
        raise RuntimeError("No calibrators available. Provide logits for Temperature or install scikit-learn for Isotonic.")

    best = min(results, key=lambda r: r[1]["ece"])
    return best  # (name, {ece,mce,cal})

# ---- CLI ----
def _load_csv(path: str):
    # Expect header with columns: confidence,label[,logit]
    import csv
    confs, labels, logits = [], [], []
    with open(path, newline="", encoding="utf-8") as f:
        for i, row in enumerate(csv.DictReader(f)):
            confs.append(float(row["confidence"]))
            labels.append(int(row["label"]))
            if "logit" in row and row["logit"] not in ("", None):
                logits.append(float(row["logit"]))
    conf = np.array(confs, dtype=float)
    y = np.array(labels, dtype=int)
    logit_arr = np.array(logits, dtype=float) if logits else None
    return conf, y, logit_arr

def main():
    ap = argparse.ArgumentParser(description="Lukhas Calibration")
    ap.add_argument("--csv", required=True, help="Path to log CSV with confidence,label[,logit]")
    ap.add_argument("--out", default=os.path.expanduser("~/.lukhas/state/calibration.json"))
    args = ap.parse_args()

    conf, y, logits = _load_csv(args.csv)
    base_ece, base_mce = ece_mce(conf, y)
    base_brier = brier_score(conf, y)

    name, info = auto_calibrate(conf, y, logits)
    # For preview, transform validation set with the chosen calibrator against original confidences/logits
    if name == "isotonic":
        cal_conf = info["cal"].transform(conf)
    else:
        if logits is None:
            raise RuntimeError("Temperature scaling chosen but logits were not provided.")
        cal_conf = info["cal"].transform(logits)

    out = {
        "chosen": name,
        "base": {"ece": base_ece, "mce": base_mce, "brier": base_brier},
        "post": {
            "ece": ece_mce(cal_conf, y)[0],
            "mce": ece_mce(cal_conf, y)[1],
            "brier": brier_score(cal_conf, y),
        },
        "params": {"T": getattr(info["cal"], "T", None)}
    }
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
