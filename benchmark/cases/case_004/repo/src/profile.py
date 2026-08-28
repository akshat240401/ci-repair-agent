def serialize_profile(record: dict) -> dict:
    return {"id":record["id"],"name":record["username"]}
