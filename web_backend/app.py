from __future__ import annotations

import base64
import io
import json
import os
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from queue import Queue
from threading import Thread

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse

from web_backend.repair_service import UploadValidationError, run_uploaded_repair

app = FastAPI(title="CI Repair Agent API", version="0.2.0")


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


PUBLIC_DEMO_ONLY = env_flag("PUBLIC_DEMO_ONLY", False)

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
    return {"status": "ok", "public_demo_only": PUBLIC_DEMO_ONLY}


def _sample_case_013_payload() -> tuple[bytes, str, str, str]:
    root = Path(__file__).resolve().parents[1]
    case_dir = root / "benchmark" / "cases" / "case_013"
    repo_dir = case_dir / "repo"
    log_path = case_dir / "failing_log.txt"
    metadata_path = case_dir / "metadata.json"

    if not repo_dir.is_dir() or not log_path.is_file() or not metadata_path.is_file():
        raise HTTPException(status_code=404, detail="Built-in sample case is unavailable")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(repo_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(repo_dir).as_posix())

    return (
        buf.getvalue(),
        metadata["targeted_test"],
        log_path.read_text(encoding="utf-8"),
        metadata.get("title", "Multi-file API contract migration"),
    )


def _stream_repair(payload: bytes, failing_log: str, targeted_test: str) -> StreamingResponse:
    q: Queue[dict | None] = Queue()
    sequence = {"value": 0}

    def progress(stage: str, message: str, data: dict | None) -> None:
        sequence["value"] += 1
        q.put({
            "type": "progress",
            "stage": stage,
            "message": message,
            "data": data,
            "sequence": sequence["value"],
            "emitted_at": datetime.now(timezone.utc).isoformat(),
        })

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
        except Exception as exc:
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


@app.get("/api/sample/case-013")
def sample_case_013() -> JSONResponse:
    payload, targeted_test, failing_log, title = _sample_case_013_payload()
    return JSONResponse({
        "filename": "case_013_repo.zip",
        "targeted_test": targeted_test,
        "failing_log": failing_log,
        "repository_zip_b64": base64.b64encode(payload).decode("ascii"),
        "title": title,
    })


@app.post("/api/sample/case-013/repair/stream")
def sample_case_013_repair_stream() -> StreamingResponse:
    payload, targeted_test, failing_log, _ = _sample_case_013_payload()
    return _stream_repair(payload, failing_log, targeted_test)


@app.post("/api/repair/stream")
async def repair_stream(
    repository: UploadFile = File(...),
    failing_log: str = Form(...),
    targeted_test: str = Form(...),
):
    if PUBLIC_DEMO_ONLY:
        raise HTTPException(
            status_code=403,
            detail="Custom repository execution is disabled on the public demo. Use the built-in sample case.",
        )
    if not repository.filename or not repository.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="repository must be a .zip file")
    payload = await repository.read()
    return _stream_repair(payload, failing_log, targeted_test)
