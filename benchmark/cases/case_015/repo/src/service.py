from src.config_writer import serialize_timeout
from src.validator import validate_timeout
def build_config(seconds):
    config = serialize_timeout(seconds)
    validate_timeout(config)
    return config
