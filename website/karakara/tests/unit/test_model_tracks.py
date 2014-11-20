import pytest

from karakara.model.model_tracks import Track


@pytest.mark.parametrize(('tags'), [
    ([]),
])
def test_track_status(tags):
    Track._status(tags)
