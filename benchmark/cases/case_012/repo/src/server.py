from src.settings import resolve_settings

def server_port(file_config, env_config):
    return resolve_settings(file_config, env_config)["port"]
