#!/bin/sh
# Container entrypoint: train the model if missing, seed if the DB is empty, then serve.
set -e
cd /app/backend
[ -f ml/artifacts/risk_model.joblib ] || python -m ml.train
python -m app.seed
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers "${WORKERS:-1}" --proxy-headers
