import contextlib
import csv
from pathlib import Path
import io
import asyncio
from collections import defaultdict
import typing as t

from .settings_manager import SettingsManager
from .queue_model import Queue, QueueItem

type QueueName = str


class QueueManager:
    def __init__(self, path: Path, settings: SettingsManager):
        assert path.is_dir()
        self.path = path
        self.settings = settings
        self.queue_async_locks: defaultdict[QueueName, asyncio.Lock] = defaultdict(asyncio.Lock)

    def path_csv(self, name: QueueName) -> Path:
        return self.path.joinpath(f"{name}.csv")

    def for_json(self, name: QueueName) -> list[dict[str, t.Any]]:
        file_context = (
            self.path_csv(name).open("r", encoding="utf8") if self.path_csv(name).is_file() else io.StringIO("")
        )
        with file_context as filehandle:
            return list(
                QueueItem.model_validate(row).model_dump(mode="json", exclude={"added_time", "debug_str"})
                for row in csv.DictReader(filehandle)
            )

    @contextlib.contextmanager
    def queue_modify_context(self, name: QueueName):
        path_csv = self.path_csv(name)
        path_csv.touch()
        with path_csv.open("r+", encoding="utf8") as filehandle:
            queue = Queue(
                [QueueItem.model_validate(row) for row in csv.DictReader(filehandle)],
                self.settings.get(name),
            )
            yield queue
            if queue.modified:
                filehandle.seek(0)
                filehandle.truncate(0)
                fields = QueueItem.model_json_schema()["properties"].keys()
                writer = csv.DictWriter(filehandle, fields)
                writer.writeheader()
                for i in queue.items:
                    writer.writerow(i.model_dump(mode="json"))

    @contextlib.asynccontextmanager
    async def async_queue_modify_context(self, name: QueueName):
        async with self.queue_async_locks[name]:
            with self.queue_modify_context(name) as queue:
                yield queue
