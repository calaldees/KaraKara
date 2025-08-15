import asyncio
import contextlib
from typing import Callable, Awaitable

import ujson as json
import sanic
from sanic.log import logger as log


async def _background_tracks_update_event(app: sanic.Sanic) -> None:
    log.debug("`tracks.json` check mtime")

    if not app.ctx.track_manager.has_tracks_updated:
        return

    log.info("`tracks.json` reload")
    app.ctx.track_manager.reload_tracks()

    tracks_json_mtime = app.ctx.track_manager.mtime

    log.info("`tracks.json` mqtt event")
    await app.ctx.mqtt.publish(
        'global/tracks-updated',
        json.dumps({'tracks_json_mtime': tracks_json_mtime}),
        retain=True,
    )


tracks_update_semaphore = asyncio.Semaphore(1)
async def background_tracks_update_event(
    app: sanic.Sanic,
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
            await _background_tracks_update_event(app)
            await _asyncio_sleep(60)
