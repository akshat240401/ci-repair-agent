from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_clean_room_smoke_writes_where_it_reads():
    text = (ROOT / "scripts" / "clean_room_check.ps1").read_text(encoding="utf-8")
    assert '"--output-dir" "results/smoke/repair_loop"' in text
    assert r"results\smoke\repair_loop\summary.json" in text
