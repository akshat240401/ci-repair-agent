from src.paths import is_within_workspace

def test_child_path_is_allowed(tmp_path):
    workspace = tmp_path / "work"
    child = workspace / "src" / "a.py"
    child.parent.mkdir(parents=True)
    child.write_text("x")
    assert is_within_workspace(workspace, child) is True

def test_sibling_with_shared_prefix_is_rejected(tmp_path):
    workspace = tmp_path / "work"
    sibling = tmp_path / "work_backup" / "secret.txt"
    sibling.parent.mkdir(parents=True)
    sibling.write_text("secret")
    assert is_within_workspace(workspace, sibling) is False
