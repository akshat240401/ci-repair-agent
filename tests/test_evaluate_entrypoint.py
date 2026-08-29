from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_evaluate_entrypoint_exists_and_has_modes():
    path = ROOT / "evaluate.py"
    assert path.exists()

    text = path.read_text(encoding="utf-8")
    assert '"deterministic"' in text
    assert '"smoke"' in text
    assert '"full"' in text
    assert "OPENAI_API_KEY" in text
    assert "evaluation.repair_loop_experiment" in text
    assert "evaluation.submission_cost_report" in text


def test_env_example_contains_no_real_key():
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "OPENAI_API_KEY=" in text
    assert "MODEL_NAME=" in text
    assert "MODEL_REASONING_EFFORT=" in text
    assert "sk-" not in text
