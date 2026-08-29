from src.release import latest_version

def test_latest_version_handles_two_digit_minor():
    assert latest_version(["2.9.0", "2.10.0", "2.8.7"]) == "2.10.0"

def test_latest_version_handles_patch_numbers():
    assert latest_version(["1.4.9", "1.4.11", "1.4.2"]) == "1.4.11"
