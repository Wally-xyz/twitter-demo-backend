import uuid


def generate_id(prefix: str, max_length: int = 31):
    base_uuid = str(uuid.uuid4())
    stripped = base_uuid.lower().replace("-", "")
    return (prefix + "_" + stripped)[:max_length]
