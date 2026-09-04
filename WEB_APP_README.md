# Usable Web App

This repository includes a browser interface for the existing CI repair engine.

## Current web-app features

1. Upload a small Python 3.11 / pytest repository as a ZIP.
2. Paste the failing CI or pytest log.
3. Enter the targeted failing pytest node ID.
4. Or click **Try sample case** to load benchmark case 013 automatically.
5. Run the existing triage, bounded investigation, transactional patch, retry, and deterministic verification workflow.
6. Follow a richer execution trace showing triage, investigation tools, repair-plan details, patch application, and each verification gate.
7. See root cause, target files, verification checks, attempts, runtime, and unified diff.
8. Download the repaired repository when the result is `VERIFIED_REPAIR`.

## Frontend security versions

The web app stays on the Next.js 15.5 release line and pins patched versions:

- Next.js 15.5.25
- React 19.1.8
- React DOM 19.1.8

After updating an existing checkout, remove the old install and reinstall so the lockfile/dependency tree is regenerated.

## Local run

### Backend

From the repository root:

```powershell
cd "C:\Users\aksha\Desktop\FILES\MY-WORK\ci-repair-agent"
.\.venv\Scripts\Activate.ps1
pip install -e .
pip install -r .\requirements-dev.txt
pip install -r .\web_backend\requirements.txt

$env:OPENAI_API_KEY="YOUR_KEY"
$env:MODEL_NAME="gpt-5.6-luna"
$env:MODEL_REASONING_EFFORT="low"
$env:WEB_ORIGINS="http://localhost:3000"
$env:PUBLIC_DEMO_ONLY="false"

uvicorn web_backend.app:app --reload --host 127.0.0.1 --port 8000
```

Health check: `http://127.0.0.1:8000/health`

### Frontend

In a second terminal:

```powershell
cd "C:\Users\aksha\Desktop\FILES\MY-WORK\ci-repair-agent\web"
Remove-Item .\node_modules -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item .\package-lock.json -Force -ErrorAction SilentlyContinue
npm install
Copy-Item .\.env.example .\.env.local -Force
# .env.local should contain NEXT_PUBLIC_DEMO_ONLY=false for local trusted-repository mode
npm run dev
```

Open `http://localhost:3000`.

## Deployment shape

- `web/` -> Vercel.
- Python project + `web_backend/` -> a container host.
- Set `NEXT_PUBLIC_API_URL` on Vercel to the backend origin.
- Set `NEXT_PUBLIC_DEMO_ONLY=true` on Vercel for the public demo.
- Set `PUBLIC_DEMO_ONLY=true` on the backend for the public demo.
- Set `OPENAI_API_KEY`, `MODEL_NAME`, `MODEL_REASONING_EFFORT`, and `WEB_ORIGINS` only on the backend.

### Public deployment mode

Use these backend environment variables:

```text
OPENAI_API_KEY=<secret>
MODEL_NAME=gpt-5.6-luna
MODEL_REASONING_EFFORT=low
PUBLIC_DEMO_ONLY=true
WEB_ORIGINS=https://<your-vercel-domain>
```

Use these Vercel environment variables:

```text
NEXT_PUBLIC_API_URL=https://<your-backend-domain>
NEXT_PUBLIC_DEMO_ONLY=true
```

With public demo mode enabled, `/api/repair/stream` rejects arbitrary uploads with HTTP 403. The browser's **Try sample case** flow uses `/api/sample/case-013/repair/stream`, which loads and executes only the repository bundled with this application.

For local trusted-repository development, keep both demo flags false.

## Important security boundary

The current backend is a **trusted-repository demo backend**. It invokes pytest on the uploaded repository because deterministic verification is part of the product. Do not expose this version to arbitrary public uploads on a shared machine.

For a public production service, move syntax/test execution into a dedicated untrusted-code sandbox/VM that has:

- no OpenAI API key or other secrets;
- no host filesystem mounts;
- no outbound network by default;
- CPU, memory, process, and wall-clock limits;
- a disposable filesystem per repair job.

The agent/control-plane calls can remain in the FastAPI service while verification executes inside that isolated worker.
