from __future__ import annotations
import re
from evaluation.result_schema import CommandResult
from src.state.hashing import sha256_text

FAILED_RE = re.compile(r"(?m)^FAILED\s+.+$")
ASSERT_RE = re.compile(r"(?m)^E\s+.+$")

def failure_signature(result: CommandResult | None) -> str:
    if result is None:
        return "NO_RESULT"
    text = f"{result.stdout}\n{result.stderr}"
    evidence = FAILED_RE.findall(text) + ASSERT_RE.findall(text)
    if not evidence:
        evidence = [f"status={result.status}", f"exit={result.exit_code}"]
    return sha256_text("\n".join(x.strip() for x in evidence[:10]))
