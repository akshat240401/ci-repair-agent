from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = [
    ".env.example",
    "evaluate.py",
    "pyproject.toml",
    "REPRODUCTION.md",
    "IMPROVEMENT_CHANGELOG.md",
    "benchmark",
    "baseline",
    "evaluation",
    "results",
    "src",
    "tests",
    "trajectories",
    "src/agents",
    "src/patching",
    "src/schemas",
    "src/state",
    "src/tools",
    "src/verification",
]


def test_submission_repository_structure():
    missing = [
        path
        for path in REQUIRED_PATHS
        if not (ROOT / path).exists()
    ]
    assert not missing, f"Missing required repository paths: {missing}"


def test_ground_truth_is_separate_from_agent_code():
    ground_truth = ROOT / "benchmark" / "ground_truth"
    assert ground_truth.exists()
    assert not (ROOT / "src" / "ground_truth").exists()
