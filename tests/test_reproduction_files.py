from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_reproduction_guide_exists():
    text = (ROOT / "REPRODUCTION.md").read_text(encoding="utf-8")
    assert "Python 3.11" in text
    assert "requirements-dev.txt" in text
    assert "pytest -q tests" in text
    assert "evaluation.evaluator --mode inspect" in text
    assert "OPENAI_API_KEY" in text
    assert "tagged `main`" in text


def test_clean_room_script_is_strict():
    text = (ROOT / "scripts" / "clean_room_check.ps1").read_text(encoding="utf-8")
    assert "Invoke-Checked" in text
    assert "$LASTEXITCODE" in text
    assert "requirements-dev.txt" in text
    assert "verified_repair_rate" in text
    assert "throw" in text


def test_dev_requirements_pin_pytest():
    text = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "pytest==8.3.5" in text
