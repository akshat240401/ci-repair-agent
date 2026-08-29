from src.artifact import output_path

def test_output_path_handles_root_with_trailing_separator():
    assert output_path("/tmp/build/", "report.json") == "/tmp/build/report.json"

def test_output_path_handles_root_without_trailing_separator():
    assert output_path("/tmp/build", "report.json") == "/tmp/build/report.json"
