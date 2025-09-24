import types
import aiomqtt
import sanic
from pathlib import Path

from .track_manager import TrackManager
from .queue_manager import QueueManagerCSVAsync
from .settings_manager import SettingsManager
from .login_manager import User


class Ctx(types.SimpleNamespace):
    mqtt: aiomqtt.Client
    path_queue: Path
    session_id: str
    user: User
    track_manager: TrackManager
    settings_manager: SettingsManager
    queue_manager: QueueManagerCSVAsync

class Config(sanic.Config):
    PATH_TRACKS: str
    PATH_QUEUE: str
    BACKGROUND_TASK_TRACK_UPDATE_ENABLED: bool
    MQTT: str | None

class App(sanic.Sanic[Config, Ctx]):
    pass

type Request = sanic.Request[App, Ctx]
