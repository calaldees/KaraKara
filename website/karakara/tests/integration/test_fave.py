from unittest.mock import patch


def test_fave_cycle(app, settings, tracks):
    """
    Test fave cycle
    Faves are stored in a client side cookie
    The fave view simply redirects to a track list with the track_id's in the url
    """
    # Add/remove test tracks
    with patch.dict(settings, {'karakara.faves.enabled': True}):
        response = app.post('/fave', {'id': 't1'})
        response = app.post('/fave', {'id': 't1', 'method': 'delete'})
        response = app.post('/fave', {'id': 't2'})
        # Check the correct tracks are in the fave view
        response = app.get('/fave')
        assert response.status_code == 302
        response = response.follow()
        assert 'track 2'     in response.text.lower()
        assert 'track 1' not in response.text.lower()
        # Check that the correct add/remove fave buttons are on the track pages
        response = app.get('/track/t1')
        assert 'Add to faves' in response.text
        response = app.get('/track/t2')
        assert 'Remove from faves' in response.text
        response = app.post('/fave', {'id': 't2', 'method': 'delete'})
        response = app.get('/track/t2')
        assert 'Add to faves' in response.text


def test_fave_disbaled(app, settings, tracks):
    # Faves disabled
    with patch.dict(settings, {'karakara.faves.enabled': False}):
        response = app.get('/fave', expect_errors=True)
        assert response.status_code == 400
        response = app.post('/fave?format=json', {'id': 't1'}, expect_errors=True)
        assert response.status_code == 400, 'faves should be disabled'
        response = app.get('/track/t1')
        assert 'faves' not in response.text.lower()
