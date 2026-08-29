from __future__ import annotations
import json
from src.schemas.patch_plan import PatchPlan
from src.state.hashing import sha256_text

def patch_plan_hash(plan: PatchPlan) -> str:
    canonical = json.dumps(plan.model_dump(), sort_keys=True, separators=(",", ":"))
    return sha256_text(canonical)
