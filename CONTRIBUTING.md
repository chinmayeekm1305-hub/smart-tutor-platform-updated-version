# Team workflow

## One-time setup (each teammate)
1. Accept the GitHub invite email from the team lead.
2. Install **Python 3.12** (tick "Add python.exe to PATH"), **Node.js LTS** and **GitHub Desktop**.
3. GitHub Desktop → **File → Clone repository** → pick `smart-tutor` → clone into `C:\Projects\smart-tutor`.
   Do not clone into a OneDrive folder.
4. Open **Command Prompt** (not PowerShell) and run each line:
   ```
   cd C:\Projects\smart-tutor\backend
   python -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   copy .env.example .env
   cd ..\frontend
   npm install
   npm run build
   cd ..\backend
   .venv\Scripts\python -m ml.train
   .venv\Scripts\python -m app.seed
   ```
5. Start the app with `.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000` and open http://localhost:8000.

To work on the website with live reload, open a second Command Prompt and run `cd C:\Projects\smart-tutor\frontend` and then `npm run dev`. Use http://localhost:5173 while editing.

## Every time you work (the golden rules)
1. **Fetch origin / Pull** in GitHub Desktop first, so you start from the latest code.
2. **Create a branch** for your task (Branch → New branch), e.g. `rahul/add-os-subject`. Never work directly on `main`.
3. Make your change and test it locally.
4. Run the tests: `cd backend` then `.venv\Scripts\python -m pytest -q`. They must all pass.
5. In GitHub Desktop, write a short summary, **Commit**, then **Push origin**.
6. Click **Create Pull Request**. The team lead reviews it and merges it into `main`.
7. Merging into `main` updates the live website automatically within about 5 minutes.

## Never commit
- The `.env` file or any API key. `.gitignore` already blocks `.env`. Share keys privately, never in chat groups.
- `node_modules`, `.venv` or `*.db` files.
