from pathlib import Path
import datetime

from api_queue.settings_manager import SettingsManager, QueueSettings


def test_settings_manager(tmp_path: Path):
    sm = SettingsManager(tmp_path)

    # room should not exist yet
    assert not sm.room_exists("test_room")

    # load defaults
    settings = sm.get("test_room")
    assert settings.title == "KaraKara"
    assert settings.track_space.total_seconds() == 15

    # make changes and save
    settings.title = "My Room"
    settings.track_space = settings.track_space * 2
    sm.set("test_room", settings)

    # room should exist after settings are first saved
    assert sm.room_exists("test_room")

    # load saved settings
    settings = sm.get("test_room")
    assert settings.title == "My Room"
    assert settings.track_space.total_seconds() == 30


def test_settings_defaults():
    # default settings
    qs = QueueSettings()
    assert qs.title == "KaraKara"
    assert qs.track_space.total_seconds() == 15


def test_settings_custom():
    # custom settings from native types
    qs = QueueSettings(
        title="Custom Room",
        track_space=datetime.timedelta(seconds=60),
        hidden_tags=["red:duplicate", "blue:test"],
        forced_tags=["green:forced"],
        preview_volume=0.5,
        coming_soon_track_count=3,
        validation_event_start_datetime=datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc),
        validation_event_end_datetime=datetime.datetime(2024, 12, 31, 23, 59, 59, tzinfo=datetime.timezone.utc),
        validation_performer_names=["Alice", "Bob"],
        auto_reorder_queue=True,
    )
    assert qs.title == "Custom Room"
    assert qs.track_space.total_seconds() == 60


def test_settings_custom_json():
    # custom settings from JSON types (ie, ints and
    # strings, not timedelta or datetime objects)
    qs = QueueSettings(
        title="Custom Room",
        track_space=60,  # pyright: ignore[reportArgumentType]
        hidden_tags=["red:duplicate", "blue:test"],
        forced_tags=["green:forced"],
        preview_volume=0.5,
        coming_soon_track_count=3,
        validation_event_start_datetime="2024-01-01T00:00:00Z",  # pyright: ignore[reportArgumentType]
        validation_event_end_datetime="2024-12-31T23:59:59Z",  # pyright: ignore[reportArgumentType]
        validation_performer_names=["Alice", "Bob"],
        auto_reorder_queue=True,
    )
    assert qs.title == "Custom Room"
    assert qs.track_space.total_seconds() == 60


def test_settings_datetime_timezones():
    # datetimes with custom timezone should be converted to UTC
    # datetime without timezone should be assumed as UTC
    qs = QueueSettings(
        validation_event_start_datetime="2024-01-01T00:00:00+02:00",  # pyright: ignore[reportArgumentType]
        validation_event_end_datetime="2024-01-01T00:08:00",  # pyright: ignore[reportArgumentType]
    )
    assert qs.validation_event_start_datetime == datetime.datetime(2023, 12, 31, 22, 0, tzinfo=datetime.timezone.utc)
    assert qs.validation_event_end_datetime == datetime.datetime(2024, 1, 1, 0, 8, tzinfo=datetime.timezone.utc)


def test_settings_invalid():
    # invalid settings should raise
    try:
        QueueSettings(
            title="Bad Room",
            track_space=-10,  # pyright: ignore[reportArgumentType]
        )
        assert False, "Expected ValueError for negative track_space"
    except ValueError:
        pass

    try:
        QueueSettings(
            title="Bad Room",
            preview_volume=1.5,
        )
        assert False, "Expected ValueError for preview_volume > 1"
    except ValueError:
        pass

    try:
        QueueSettings(
            title="Bad Room",
            coming_soon_track_count=0,
        )
        assert False, "Expected ValueError for coming_soon_track_count <= 0"
    except ValueError:
        pass
