import asyncio
import contextlib
import datetime
from functools import reduce
from pathlib import Path
from collections.abc import MutableMapping, Collection
from typing import Callable, Awaitable

import sanic
from sanic.log import logger as log


async def _background_tracks_update_event(
    app: sanic.Sanic,
    push_settings_to_mqtt: Callable[[sanic.Sanic, str], contextlib.AbstractAsyncContextManager[None]],
) -> None:
    log.debug("`tracks.json` check mtime")

    if not app.ctx.track_manager.has_tracks_updated:
        return

    log.info("`tracks.json` reload")
    app.ctx.track_manager.reload_tracks()
    app.ctx.settings_manager.global_settings.tracks_json_mtime = app.ctx.track_manager.mtime

    # Part Hack - Part Keeping it Simple
    # The queue models use files on the filesystem
    # Rather than abstracting 'platform independent' queue name lists,
    #   I've decided to look at the filesystem here.
    TIMESTAMP_ACTIVE_THRESHOLD = (datetime.datetime.now() - datetime.timedelta(days=1)).timestamp()
    def _reducer(acc: MutableMapping[str, float], file: Path):
        """
        A queue could be classed as `active` with the mtime of `xxx.csv` or `xxx_settings.json`.
        Normalise track names and get highest mtime
        """
        if file.suffix != ".csv" and not file.name.endswith("_settings.json"):
            return acc
        name = file.stem.removesuffix("_settings")
        mtime = file.stat().st_mtime
        if mtime > acc.get(name, TIMESTAMP_ACTIVE_THRESHOLD):
            acc[name] = mtime
        return acc
    active_room_names: Collection[str] = reduce(_reducer, app.ctx.path_queue.iterdir(), {}).keys()

    if not active_room_names:
        log.info("no currently active_room_names to notify of `tracks.json` update event")
        return

    log.info(f"`tracks.json` notifying {active_room_names=}")
    for room_name in active_room_names:
        async with push_settings_to_mqtt(app, room_name):
            pass  # the context manager will trigger the send


tracks_update_semaphore = asyncio.Semaphore(1)
async def background_tracks_update_event(
    app: sanic.Sanic,
    push_settings_to_mqtt: Callable[[sanic.Sanic, str], contextlib.AbstractAsyncContextManager[None]],
    _asyncio_sleep: Callable[[int], Awaitable[None]] = asyncio.sleep,
) -> None:
    # A background task is created for each sanic worker - Only allow one background process by aborting if another task has the semaphore
    # WARNING?! I don't think this works. Workers are NOT async tasks, they are threads, so the asyncio.semaphore does nothing
    if tracks_update_semaphore.locked():
        log.debug("`tracks.json` background_tracks_update_event already active - cancel task")
        return
    async with tracks_update_semaphore:
        log.info('background_tracks_update_event started')
        while app.config.BACKGROUND_TASK_TRACK_UPDATE_ENABLED:
            await _background_tracks_update_event(app, push_settings_to_mqtt)
            await _asyncio_sleep(60)
