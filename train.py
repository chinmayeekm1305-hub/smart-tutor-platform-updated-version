"""Train the student-performance (at-risk) model.

Real student data isn't available at project start, so we simulate a realistic cohort:
each simulated learner has a hidden ability and diligence; their quiz behaviour (the same
features the app computes) is generated from those, and the label is whether their
end-of-term exam score falls below 40%. Once the app collects real attempts, run
`python -m ml.train --from-db` to retrain on real students.

Outputs: ml/artifacts/risk_model.joblib and ml/artifacts/metrics.json
Run:  python -m ml.train
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.features import FEATURES  # noqa: E402

ART = Path(__file__).parent / "artifacts"


def simulate(n: int = 4000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ability = rng.beta(2.2, 2.0, n)            # hidden skill, 0..1
    diligence = rng.beta(2.0, 2.0, n)          # hidden effort, 0..1
    growth = rng.normal(0, 0.08, n) + 0.1 * (diligence - 0.5)

    n_attempts = rng.poisson(15 + 110 * diligence) + 1
    accuracy = np.clip(0.2 + 0.7 * ability + rng.normal(0, 0.07, n), 0, 1)
    easy_acc = np.clip(accuracy + 0.15 + rng.normal(0, 0.06, n), 0, 1)
    hard_acc = np.clip(accuracy - 0.25 + 0.15 * ability + rng.normal(0, 0.08, n), 0, 1)
    # last-10-answers accuracy is a small sample, so it is noisy (binomial), just like in the real app
    recent = rng.binomial(10, np.clip(accuracy + growth + 0.08, 0, 1)) / 10
    trend = recent - accuracy
    avg_time = np.clip(48 - 22 * ability + rng.normal(0, 7, n), 6, 120)
    study_min = np.clip(rng.gamma(2 + 6 * diligence, 12), 0, 600)
    mastery = np.clip(0.05 + 0.9 * (0.8 * ability + 0.2 * recent) + rng.normal(0, 0.08, n), 0.02, 0.97)
    active_days = np.clip(rng.poisson(2 + 12 * diligence), 1, 30)

    exam = (100 * (0.55 * ability + 0.2 * diligence + 0.15 * np.clip(growth + 0.5, 0, 1))
            + rng.normal(0, 7, n))
    df = pd.DataFrame({
        "accuracy": accuracy, "easy_accuracy": easy_acc, "hard_accuracy": hard_acc,
        "recent_accuracy": recent, "trend": trend, "avg_time": avg_time, "n_attempts": n_attempts,
        "study_minutes": study_min, "mastery_avg": mastery, "active_days": active_days,
    })
    df["at_risk"] = (exam < 40).astype(int)
    return df


def from_db() -> pd.DataFrame:
    """Build a training set from real students. Label = mastery below 0.45 (proxy until exam marks exist)."""
    from app.database import SessionLocal
    from app.models import User
    from app.services.features import student_features
    db = SessionLocal()
    rows = []
    for u in db.query(User).filter(User.role == "student"):
        f = student_features(db, u.id)
        if f["n_attempts"] >= 5:
            f["at_risk"] = int(f["mastery_avg"] < 0.45)
            rows.append(f)
    db.close()
    return pd.DataFrame(rows)


def train(df: pd.DataFrame) -> dict:
    X, y = df[FEATURES], df["at_risk"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=7, stratify=y)

    models = {
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "random_forest": RandomForestClassifier(n_estimators=300, max_depth=8, min_samples_leaf=5,
                                                class_weight="balanced", random_state=7),
    }
    results = {}
    for name, m in models.items():
        m.fit(Xtr, ytr)
        p = m.predict_proba(Xte)[:, 1]
        pred = (p >= 0.5).astype(int)
        results[name] = {"accuracy": round(accuracy_score(yte, pred), 4),
                         "f1": round(f1_score(yte, pred), 4),
                         "roc_auc": round(roc_auc_score(yte, p), 4)}
        print(f"\n== {name} ==\n" + classification_report(yte, pred, target_names=["on track", "at risk"]))

    best_name = max(results, key=lambda k: results[k]["roc_auc"])
    best = models[best_name]
    ART.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": best, "features": FEATURES, "name": best_name}, ART / "risk_model.joblib")

    importances = {}
    if hasattr(best, "feature_importances_"):
        importances = dict(sorted(zip(FEATURES, map(float, best.feature_importances_)), key=lambda x: -x[1]))
    else:
        coef = best[-1].coef_[0]
        importances = dict(sorted(zip(FEATURES, map(lambda c: abs(float(c)), coef)), key=lambda x: -x[1]))
    metrics = {"selected_model": best_name, "n_samples": len(df), "positive_rate": round(float(y.mean()), 3),
               "results": results, "feature_importance": {k: round(v, 4) for k, v in importances.items()}}
    (ART / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\nSaved {best_name} -> {ART/'risk_model.joblib'}")
    print(json.dumps(results, indent=2))
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-db", action="store_true", help="train on real students in the database")
    args = ap.parse_args()
    data = from_db() if args.from_db else simulate()
    if len(data) < 30:
        raise SystemExit("Not enough real students yet (need 30+ with 5+ attempts). Use simulated training.")
    train(data)
