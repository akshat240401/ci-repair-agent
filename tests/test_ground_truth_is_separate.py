from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_ground_truth_not_inside_agent_visible_repos():
    for repo in (ROOT/'benchmark'/'cases').glob('case_*/repo'):
        assert not list(repo.rglob('*ground_truth*'))
