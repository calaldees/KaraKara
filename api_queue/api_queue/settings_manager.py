from pathlib import Path

from .types import Settings as QueueSettings

class SettingsManager:
    def __init__(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)  # is this safe?
        assert path.is_dir()
        self.path = path

    def room_exists(self, name: str) -> bool:
        return self.path.joinpath(f"{name}_settings.json").is_file()

    def set(self, name: str, settings: QueueSettings) -> None:
        path = self.path.joinpath(f"{name}_settings.json")
        json_str = settings.model_dump_json()
        path.write_text(json_str)

    def get(self, name: str) -> QueueSettings:
        path = self.path.joinpath(f"{name}_settings.json")
        if path.is_file():
            return QueueSettings.model_validate_json(path.read_text())
        return QueueSettings()
