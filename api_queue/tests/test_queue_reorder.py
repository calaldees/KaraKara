import pytest
import datetime

from api_queue.queue_model import Queue, QueueItem
from api_queue.queue_updated_actions import reorder

ONE_MINUTE = datetime.timedelta(seconds=60)


def _mins_ago(minutes: int) -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.timezone.utc) - datetime.timedelta(minutes=minutes)


def qi(name: str, duration: datetime.timedelta, session: str, performer: str, **kwargs) -> QueueItem:
    return QueueItem.model_validate(
        {"track_id": name, "track_duration": duration, "session_id": session, "performer_name": performer} | kwargs
    )


@pytest.fixture
def qu(qu: Queue):
    qu._now = None
    qu.settings.coming_soon_track_count = 3
    return qu


def test_empty_reorder(qu: Queue):
    reorder(qu)


def test_no_reorder__tracks_within_coming_soon_track_count(qu: Queue):
    qu.add(qi("Track1", ONE_MINUTE, "TestSession1", "test_name1", added_time=_mins_ago(60)))
    qu.add(qi("Track2", ONE_MINUTE, "TestSession2", "test_name2", added_time=_mins_ago(50)))
    qu.add(qi("Track3", ONE_MINUTE, "TestSession3", "test_name3", added_time=_mins_ago(40)))
    reorder(qu)
    assert [i.track_id for i in qu.future] == ["Track1", "Track2", "Track3"]


def test_no_reorder(qu: Queue):
    """
    no_reorder - 6 tracks queued by 6 different people
    """
    qu.add(qi("Track1", ONE_MINUTE, "TestSession1", "test_name1", added_time=_mins_ago(60)))
    qu.add(qi("Track2", ONE_MINUTE, "TestSession2", "test_name2", added_time=_mins_ago(50)))
    qu.add(qi("Track3", ONE_MINUTE, "TestSession3", "test_name3", added_time=_mins_ago(40)))
    qu.add(qi("Track4", ONE_MINUTE, "TestSession1", "test_name4", added_time=_mins_ago(30)))
    qu.add(qi("Track5", ONE_MINUTE, "TestSession2", "test_name5", added_time=_mins_ago(20)))
    qu.add(qi("Track6", ONE_MINUTE, "TestSession3", "test_name6", added_time=_mins_ago(10)))
    reorder(qu)
    assert [i.track_id for i in qu.future] == ["Track1", "Track2", "Track3", "Track4", "Track5", "Track6"]


def test_no_reorder_protect_coming_soon_track_count(qu: Queue):
    qu.add(qi("Track1", ONE_MINUTE, "TestSession1", "test_name1", added_time=_mins_ago(60), start_time=_mins_ago(10)))
    qu.add(qi("Track2", ONE_MINUTE, "TestSession2", "test_name2", added_time=_mins_ago(50), start_time=_mins_ago(5)))
    qu.add(qi("Track3", ONE_MINUTE, "TestSession3", "test_name3", added_time=_mins_ago(40)))
    qu.add(qi("Track4", ONE_MINUTE, "TestSession1", "test_name4", added_time=_mins_ago(30)))
    # test_name1 has sung before and should be outranked by all the others ... BUT it is currently in the protected 'coming_soon_track_count'
    qu.add(qi("Track11", ONE_MINUTE, "TestSession1", "test_name1", added_time=_mins_ago(20)))
    qu.add(qi("Track5", ONE_MINUTE, "TestSession3", "test_name5", added_time=_mins_ago(10)))
    reorder(qu)
    assert [i.track_id for i in qu.future] == ["Track3", "Track4", "Track11", "Track5"]


def test_reorder_1(qu: Queue):
    qu.add(qi("Track1", ONE_MINUTE, "TestSession1", "test_name1", added_time=_mins_ago(60), start_time=_mins_ago(10)))
    qu.add(qi("Track2", ONE_MINUTE, "TestSession2", "test_name2", added_time=_mins_ago(50), start_time=_mins_ago(5)))
    qu.add(qi("Track3", ONE_MINUTE, "TestSession3", "test_name3", added_time=_mins_ago(40)))
    qu.add(qi("Track4", ONE_MINUTE, "TestSession1", "test_name4", added_time=_mins_ago(30)))
    qu.add(qi("Track5", ONE_MINUTE, "TestSession3", "test_name5", added_time=_mins_ago(20)))
    # test_name1(Track11) has sung before and should be outranked by all the others - Track11 should be last in queue
    qu.add(qi("Track11", ONE_MINUTE, "TestSession1", "test_name1", added_time=_mins_ago(20)))
    qu.add(qi("Track6", ONE_MINUTE, "TestSession6", "test_name6", added_time=_mins_ago(10)))
    reorder(qu)
    assert [i.track_id for i in qu.future] == ["Track3", "Track4", "Track5", "Track6", "Track11"]


def test_reorder_multiple_items_in_queue(qu: Queue):
    """
    `test_name1` has two tracks in the queue (Track1 and Track11) - the second track (Track11) should be last in the queue
    """
    qu.add(qi("Track1", ONE_MINUTE, "TestSession1", "test_name1", added_time=_mins_ago(60)))
    qu.add(qi("Track2", ONE_MINUTE, "TestSession2", "test_name2", added_time=_mins_ago(50)))
    qu.add(qi("Track3", ONE_MINUTE, "TestSession3", "test_name3", added_time=_mins_ago(40)))
    qu.add(qi("Track4", ONE_MINUTE, "TestSession3", "test_name4", added_time=_mins_ago(40)))
    qu.add(qi("Track11", ONE_MINUTE, "TestSession1", "test_name1", added_time=_mins_ago(30)))
    qu.add(qi("Track5", ONE_MINUTE, "TestSession2", "test_name5", added_time=_mins_ago(20)))
    qu.add(qi("Track6", ONE_MINUTE, "TestSession3", "test_name6", added_time=_mins_ago(10)))
    reorder(qu)
    # While both Track1+Track11 are speculative, the order will not change
    assert [i.track_id for i in qu.future] == ["Track1", "Track2", "Track3", "Track4", "Track11", "Track5", "Track6"]
    # but when Track1 is played, it detects that `test_name1` has sung before and bumps Track11 down the list
    qu.items[0].start_time = _mins_ago(5)
    reorder(qu)
    assert [i.track_id for i in qu.future] == ["Track2", "Track3", "Track4", "Track5", "Track6", "Track11"]
