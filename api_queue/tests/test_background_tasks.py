import os
import json
from unittest.mock import AsyncMock
from pathlib import Path

import pytest
import sanic

from api_queue.background_tasks import _background_tracks_update_event


@pytest.mark.asyncio
async def test_background_tracks_update_event(app: sanic.Sanic, mock_mqtt: AsyncMock) -> None:
    await app.asgi_client.get('/')  # needed to kickstart `before_start` events and setup track_manager/settings_manager

    # `tracks.json` mtime should not have changed since server start. Background task should do nothing
    mock_mqtt.publish.assert_not_awaited()
    await _background_tracks_update_event(app)
    mock_mqtt.publish.assert_not_awaited()

    # Wind the clock back on `tracks.json` mtime to trigger file reload in background task
    tracks_json: Path = app.ctx.track_manager.path
    tracks_json_mtime: float = tracks_json.stat().st_mtime
    tracks_json_mtime += -1
    os.utime(tracks_json, times=(tracks_json_mtime,tracks_json_mtime))

    mock_mqtt.publish.assert_not_awaited()
    await _background_tracks_update_event(app)
    assert mock_mqtt.publish.await_count == 1

    channel, payload = mock_mqtt.publish.await_args.args
    payload = json.loads(payload)
    assert channel == 'global/tracks-updated'
    assert payload['tracks_json_mtime'] == tracks_json_mtime
