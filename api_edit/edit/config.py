import os
import dataclasses
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class AppConfig:
    path_source: Path


def init_config_from_env(debug: bool) -> AppConfig:
    logger.info("Init AppConfig from ENV")

    path_media = Path(os.getenv("PATH_HOST_media", ""))
    path_source = path_media.joinpath("source")
    if not path_source.exists:
        raise ValueError(f"{path_source} does not exist")

    return AppConfig(path_source=path_source)
