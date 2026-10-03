#!/usr/bin/env bash
# One-click local demo for macOS/Linux. Needs Python 3.10+ and Node.js 18+.
set -e
cd "$(dirname "$0")"
[ -d backend/.venv ] || python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -q -r backend/requirements.txt
[ -f backend/.env ] || cp backend/.env.example backend/.env
(cd frontend && { [ -d node_modules ] || npm install --no-audit --no-fund; } && npm run build)
cd backend
[ -f ml/artifacts/risk_model.joblib ] || python -m ml.train
python -m app.seed
echo "Smart Tutor running at http://localhost:8000"
python -m uvicorn app.main:app --port 8000
