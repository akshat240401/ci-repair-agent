from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def test_readme_covers_judging_story():
    text = read("README.md")
    required = [
        "Problem & user value",
        "Primary metric",
        "Why agents?",
        "Current measured development result",
        "Hot take",
        "Reproducibility status",
        "NO_CODE_PATCH_REQUIRED",
        "88.3%",
        "100.0%",
        "+11.7",
    ]
    for phrase in required:
        assert phrase in text


def test_changelog_contains_removed_experiment_and_evidence():
    text = read("IMPROVEMENT_CHANGELOG.md")
    assert "Log preprocessing" in text
    assert "0.0 pp improvement" in text
    assert "Multi-file transactional patch plan" in text
    assert "Clean-room reproduction" in text
    assert "Hot take" in text


def test_reproduction_has_exact_baseline_and_solution_commands():
    text = read("REPRODUCTION.md")
    required = [
        "python -m evaluation.baseline_runner",
        "python -m evaluation.quality_gate --runs 3",
        "python .\\evaluate.py --mode smoke --case case_010",
        "python .\\evaluate.py --mode full",
        "clean_room_check.ps1",
        "requirements-dev.txt",
        "benchmark/ground_truth/",
        "tag the exact submission commit",
    ]
    for phrase in required:
        assert phrase in text


def test_docs_do_not_contain_secret_like_key():
    combined = "\n".join([
        read("README.md"),
        read("REPRODUCTION.md"),
        read("IMPROVEMENT_CHANGELOG.md"),
    ])
    assert "sk-" not in combined
