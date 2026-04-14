from collections.abc import Iterable
from pathlib import Path
from typing import Generator


class FileModel:
    def __init__(self, path_source: Path):
        self.path_source = path_source
        if not self.path_source.exists():
            raise Exception(f"{path_source} does not exist on filesystem")

    @property
    def files(self) -> Iterable[Path]:
        def _text_files(path: Path) -> Generator[Path]:
            for root, dirs, files in path.walk(follow_symlinks=False):
                for file_str in files:
                    file = root.joinpath(file_str)
                    if file.suffix not in (".txt", ".srt"):
                        continue
                    yield file.relative_to(path)

        return sorted(_text_files(self.path_source))

    def _get_file(self, path: Path) -> Path:
        file_path = self.path_source.joinpath(path)
        if not file_path.exists():
            raise FileNotFoundError(path)
        return file_path

    def _get_file_backup(self, path: Path) -> Path:
        # TODO: This is a weak strategy - consider some form of rotation
        for backup_number in range(99):
            backup_path = path.with_name(path.name + f".{backup_number}.old")
            if not backup_path.exists():
                return backup_path
        raise Exception("all backup slots taken")

    def file_read(self, path: Path) -> str:
        return self._get_file(path).read_text()

    def file_write(self, path: Path, data: str) -> None:
        file_path = self._get_file(path)
        file_path_backup = self._get_file_backup(file_path)
        file_path.copy(file_path_backup)
        file_path.write_text(data)
