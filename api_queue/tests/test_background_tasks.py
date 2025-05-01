import re
import os
import json
from unittest.mock import AsyncMock
from pathlib import Path

import pytest
import sanic

from api_queue.background_tasks import _background_tracks_update_event
from api_queue.server import push_settings_to_mqtt


@pytest.mark.asyncio
async def test_background_tracks_update_event(app: sanic.Sanic, mock_mqtt: AsyncMock) -> None:
    await app.asgi_client.get('/')  # needed to kickstart `before_start` events and setup track_manager/settings_manager

    assert app.ctx.settings_manager.path == app.ctx.queue_manager.path, "assumed that local filestore for settings and queues is the same - this is an implementation detail that the test relies on and probably needs thinking about"
    path_queue: Path = app.ctx.settings_manager.path

    # `tracks.json` mtime should not have changed since server start. Background task should do nothing
    mock_mqtt.publish.assert_not_awaited()
    await _background_tracks_update_event(app, push_settings_to_mqtt)
    mock_mqtt.publish.assert_not_awaited()

    # Wind the clock back on `tracks.json` mtime to trigger file reload in background task
    tracks_json: Path = app.ctx.track_manager.path
    tracks_json_mtime: float = tracks_json.stat().st_mtime
    tracks_json_mtime += -1
    os.utime(tracks_json, times=(tracks_json_mtime,tracks_json_mtime))

    # Create a few rooms + settings files that count as `active_room_names` by jibbling mtimes of files
    path_queue.joinpath('fake_room_for_background_task_test.csv').write_text('')
    path_queue.joinpath('fake_settings_for_background_task_test_settings.json').write_text('{}')
    EXPECTED_ROOM_NAMES = frozenset({
        'fake_room_for_background_task_test',
        'fake_settings_for_background_task_test',
    })
    # Old room file should not be selected
    old_room = path_queue.joinpath('fake_old_room.csv')
    old_room.write_text('should not be part of mqtt notifications')
    os.utime(old_room, times=(tracks_json_mtime-1000000,tracks_json_mtime-1000000))

    mock_mqtt.publish.assert_not_awaited()
    await _background_tracks_update_event(app, push_settings_to_mqtt)
    assert mock_mqtt.publish.await_count == 2

    for call in mock_mqtt.publish.await_args_list:
        queue_path, settings = call.args

        queue_name = re.match('.+/(.+)/.+', queue_path).group(1)  # type: ignore[union-attr]
        assert queue_name in EXPECTED_ROOM_NAMES

        settings = json.loads(settings)
        assert settings['tracks_json_mtime'] == tracks_json_mtime
