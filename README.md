# Smart Tutor Platform
### Combining Artificial & Natural Intelligence for Adaptive Learning

An adaptive learning web app. **AI** personalises notes, quizzes and feedback for every student.
**Natural Intelligence** (teachers) reviews the AI, answers escalated doubts and mentors students the ML model flags as at risk.

Subjects included: **Python Programming, DBMS, Quantitative Aptitude** (12 topics, 120 hand-checked MCQs, notes at three levels).

---

## Quick start (local demo, about 5 minutes)

**You need:** Python 3.10+ and Node.js 18+.

| Windows | macOS / Linux |
|---|---|
| Double-click **`run_demo.bat`** | `./run_demo.sh` |

Then open **http://localhost:8000** and use the one-click demo buttons:

| Role | Email | Password |
|---|---|---|
| Student | `student@smarttutor.edu` | `student123` |
| Teacher | `teacher@smarttutor.edu` | `teacher123` |

Teacher self-registration needs the invite code `CIT-TEACHER` (change it in `backend/app/routers/auth.py`).

### Turn on the real LLM (GPT or Claude)
Edit `backend/.env` (created from `.env.example` on the first run):
```
OPENAI_API_KEY=sk-...          # or
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=auto              # picks whichever key is present
```
Restart the app. With no key, everything still works in **offline mode**: the tutor answers from the course notes using TF-IDF retrieval, and question generation builds fill-in-the-blank MCQs from the notes.

---

## Manual setup (for development)

```bash
# Backend (API on :8000, docs at http://localhost:8000/docs)
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python -m ml.train            # trains the at-risk model, prints metrics
python -m app.seed --reset    # content + 23 demo students with 3 weeks of history
uvicorn app.main:app --reload

# Frontend (hot reload on :5173, proxies /api to :8000)
cd frontend
npm install
npm run dev
```

Run the tests: `cd backend && python -m pytest -q` (12 end-to-end API tests).

---

## Free public website (Render + Neon)

1. **Database:** create a free project at [neon.com](https://neon.com) and copy the connection string (`postgresql://...`).
2. **App:** at [render.com](https://render.com), choose New → **Blueprint**, connect this GitHub repository, and Render reads `render.yaml`.
3. When asked, paste `DATABASE_URL` (from Neon), `TEACHER_INVITE_CODE` and optionally `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`.
4. Wait about 10 minutes for the first build. You get a link like `https://smart-tutor-xxxx.onrender.com`.
5. Every merge into `main` redeploys automatically.

**Free-plan notes:** the site sleeps after 15 minutes without visitors, and the first visit then takes about a minute to wake up. Open it a few minutes before a demo.
For a real pilot, set `SEED_DEMO_STUDENTS=false` (no fake students, demo buttons hidden), then log in as `teacher@smarttutor.edu` and **change the password**.

Team workflow: see [CONTRIBUTING.md](CONTRIBUTING.md).

## Production deployment with Docker (own server)

```bash
cp backend/.env.example .env        # set SECRET_KEY and an LLM key
docker compose up --build -d        # PostgreSQL + app at http://localhost:8000
```

The single Docker image builds the React app and serves it from FastAPI, so you deploy one service plus a database.
It runs on any container host (Render, Railway, Fly.io, AWS ECS, Azure Container Apps). Set `DATABASE_URL` to a managed PostgreSQL instance.

**Before going live:**

1. Set a long random `SECRET_KEY`.
2. Change the demo passwords and the teacher invite code.
3. Use HTTPS (your host's TLS, or a reverse proxy).
4. Restrict `CORS_ORIGINS` to your domain.
5. Back up the database.

---

## Project structure
```
smart-tutor/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app (also serves the built frontend)
│   │   ├── models.py            Database tables
│   │   ├── auth.py              bcrypt passwords, JWT tokens, role checks
│   │   ├── routers/             auth · content · quiz · student · tutor · teacher
│   │   ├── services/
│   │   │   ├── adaptive.py      Bayesian Knowledge Tracing, difficulty selection, recommendations
│   │   │   ├── features.py      Learning-behaviour features per student
│   │   │   ├── ml.py            At-risk prediction + K-Means learner clustering
│   │   │   └── llm.py           OpenAI / Claude / offline NLP fallback
│   │   └── seed/                Course content (notes + MCQs) and demo data
│   ├── ml/train.py              Model training and evaluation
│   └── tests/test_api.py
├── frontend/                    React + Vite + Tailwind + Recharts
├── Dockerfile · docker-compose.yml
├── run_demo.bat · run_demo.sh
└── docs/PROJECT_GUIDE.md        Architecture, algorithms, demo script, viva prep
```

See **[docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md)** for how each synopsis module is implemented, the algorithms, a 7-minute demo script and likely viva questions.
