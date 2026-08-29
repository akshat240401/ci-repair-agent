from src.release import latest_version

def select_release(records):
    return latest_version([record["version"] for record in records])
