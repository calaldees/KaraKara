## -*- coding: utf-8 -*-

import pytest

from karakara.model import DBSession, commit
from karakara.model.model_queue import Queue, QueueSetting

from karakara.views import cache


@pytest.yield_fixture(scope='session')
def queue(request, DBSession, commit):
    QUEUE_ID = 'qtest'

    queue = Queue(id=QUEUE_ID)
    DBSession.add(queue)

    queue_setting = QueueSetting()
    queue_setting.queue_id = QUEUE_ID
    queue_setting.key = 'karakara.private.password'
    queue_setting.value = QUEUE_ID
    DBSession.add(queue_setting)

    commit()
    cache.invalidate()
    yield QUEUE_ID
    DBSession.delete(queue)
