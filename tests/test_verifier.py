from pathlib import Path

from src.verification.verifier import verify_patch


def test_verifier_accepts_passing_repo(tmp_path: Path):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "src" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "src" / "calc.py").write_text(
        "def add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_calc.py").write_text(
        "from src.calc import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    result = verify_patch(repo, "tests/test_calc.py::test_add")

    assert result.syntax_passed is True
    assert result.targeted_test_passed is True
    assert result.full_suite_passed is True
