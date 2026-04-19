import logging
from collections.abc import Iterable
from pathlib import Path
from typing import Generator

logger = logging.getLogger(__name__)

FILE_EXTS = (".txt", ".srt")


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
                    if file.suffix not in FILE_EXTS:
                        continue
                    yield file.relative_to(path)

        return sorted(_text_files(self.path_source))

    def _get_file(self, path: Path) -> Path:
        file_path = self.path_source.joinpath(path)
        if not file_path.exists():
            raise FileNotFoundError(path)
        return file_path

    def _get_file_backup(self, path: Path) -> Path:
        return next(iter(
            sorted(
                (
                    path.with_name(path.name + f".{backup_number}.old")
                    for backup_number in range(3)
                ),
                key=lambda path: path.stat().st_mtime if path.exists() else 0,
            )
        ))

    def file_read(self, path: Path) -> str:
        logger.debug('file_read - %s', path)
        return self._get_file(path).read_text()

    def file_write(self, path: Path, data: str) -> None:
        if self.file_read(path) == data:
            logger.debug('File content unchanged - abort save - %s', path)
            return
        file_path = self._get_file(path)
        file_path_backup = self._get_file_backup(file_path)
        file_path.copy(file_path_backup)
        file_path.write_text(data)
        logger.debug('file_write - %s', path)
