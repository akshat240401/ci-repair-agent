from evaluation.case_loader import get_case
from src.agents.triage_agent import build_triage_input


def test_triage_input_contains_log_and_manifest_but_not_ground_truth():
    case = get_case("case_013")
    text = build_triage_input(case)

    assert "FAILING CI LOG" in text
    assert "src/producer.py" in text
    assert "src/consumer.py" in text
    assert "ground_truth" not in text
