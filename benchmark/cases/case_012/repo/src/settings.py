DEFAULTS = {
    "host": "127.0.0.1",
    "port": 8000,
    "debug": False,
}

def resolve_settings(file_config, env_config):
    return {**DEFAULTS, **env_config, **file_config}
