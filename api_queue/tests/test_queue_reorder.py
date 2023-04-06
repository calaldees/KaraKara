from api_queue.queue_reorder import reorder

def test_empty_reorder(qu):
    assert reorder(qu) is None
