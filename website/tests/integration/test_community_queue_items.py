
from .test_community import community_login

from ..data.tracks import create_test_track
from .test_queue_items import QueueManager, queue_manager

from karakara.model.actions import delete_track
from karakara.model.model_queue import QueueItem


def test_community_queue_items(app, queue, queue_manager, users, tracks, DBSession, commit):
    url = f'/community/queue_items/{queue}'

    response = app.get(url, expect_errors=True)
    assert response.status_code == 403

    #create_test_track(id='del_test')
    #commit()
    #queue_manager.add_queue_item(track_id='del_test', performer_name='test_community_queue_items')
    #queue_item_id = queue_manager.items[0]['id']

    with community_login(app):
        response = app.get(url)
        #assert False
        #delete_track(track_id='del_test')

