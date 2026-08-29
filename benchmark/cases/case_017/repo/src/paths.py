from pathlib import Path
def is_within_workspace(workspace, candidate):
    workspace = str(Path(workspace).resolve())
    candidate = str(Path(candidate).resolve())
    return candidate.startswith(workspace)
