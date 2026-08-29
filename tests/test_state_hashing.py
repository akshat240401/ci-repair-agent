from pathlib import Path
from src.state.hashing import repo_state_hash

def test_repo_state_hash_changes_with_content(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    f = repo / "a.py"
    f.write_text("x = 1\n", encoding="utf-8")
    a = repo_state_hash(repo)
    f.write_text("x = 2\n", encoding="utf-8")
    b = repo_state_hash(repo)
    assert a != b
