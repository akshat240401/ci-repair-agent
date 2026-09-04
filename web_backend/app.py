from __future__ import annotations

import json
import os
from queue import Queue
from threading import Thread

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from web_backend.repair_service import UploadValidationError, run_uploaded_repair

app = FastAPI(title="CI Repair Agent API", version="0.1.0")

origins = [x.strip() for x in os.getenv("WEB_ORIGINS", "http://localhost:3000").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/repair/stream")
async def repair_stream(
    repository: UploadFile = File(...),
    failing_log: str = Form(...),
    targeted_test: str = Form(...),
):
    if not repository.filename or not repository.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="repository must be a .zip file")
    payload = await repository.read()

    q: Queue[dict | None] = Queue()

    def progress(stage: str, message: str, data: dict | None) -> None:
        q.put({"type": "progress", "stage": stage, "message": message, "data": data})

    def worker() -> None:
        try:
            result = run_uploaded_repair(
                repo_zip=payload,
                failing_log=failing_log,
                targeted_test=targeted_test,
                progress=progress,
            )
            q.put({"type": "result", "result": result})
        except UploadValidationError as exc:
            q.put({"type": "error", "message": str(exc), "kind": "validation"})
        except Exception as exc:  # surfaced as a controlled app error, not a traceback
            q.put({"type": "error", "message": str(exc), "kind": "runtime"})
        finally:
            q.put(None)

    Thread(target=worker, daemon=True).start()

    def generate():
        while True:
            item = q.get()
            if item is None:
                return
            yield json.dumps(item, ensure_ascii=False) + "\n"

    return StreamingResponse(generate(), media_type="application/x-ndjson")
