from src.orchestration.no_code_policy import evaluate_no_code_patch
from src.schemas.triage import TriageResult


def test_config_only_failure_bypasses_code_patch():
    triage = TriageResult(
        failure_type="ENVIRONMENT_CONFIG",
        confidence=0.99,
        evidence=["CI runner is missing required environment variable SERVICE_TOKEN"],
        target_files=[],
        suspected_root_cause="Required CI environment variable is absent",
        next_step="configure SERVICE_TOKEN in CI environment",
    )
    decision = evaluate_no_code_patch(triage)
    assert decision is not None
    assert decision.status == "NO_CODE_PATCH_REQUIRED"
    assert "no repository files" in decision.reason


def test_config_failure_with_repo_target_does_not_bypass():
    triage = TriageResult(
        failure_type="ENVIRONMENT_CONFIG",
        confidence=0.95,
        evidence=["default issuer in settings.py is inconsistent"],
        target_files=["src/settings.py"],
        suspected_root_cause="repository configuration contract is wrong",
        next_step="inspect repository config implementation",
    )
    assert evaluate_no_code_patch(triage) is None


def test_logic_bug_never_uses_no_code_bypass():
    triage = TriageResult(
        failure_type="LOGIC_BUG",
        confidence=0.95,
        evidence=["assertion failure"],
        target_files=[],
        suspected_root_cause="logic error",
        next_step="investigate code",
    )
    assert evaluate_no_code_patch(triage) is None
