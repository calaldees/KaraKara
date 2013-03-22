

def test_fave_cycle(app, tracks):
    """
    Test fave cycle
    Faves are stored in a client side cookie
    The fave view simply redirects to a track list with the track_id's in the url
    """
    # Add/remove test tracks
    response = app.post('/fave?format=json', {'id':'t1'})
    response = app.post('/fave?format=json', {'id':'t1', 'method':'delete'})
    response = app.post('/fave?format=json', {'id':'t2'})
    # Check the correct tracks are in the fave view
    response = app.get('/fave')
    assert response.status_code == 302
    response = response.follow()
    assert 'track 2'     in response.text
    assert 'track 1' not in response.text
    # Check that the correct add/remove fave buttons are on the track pages
    response = app.get('/track/t1')
    assert 'Add to faves'
    response = app.get('/track/t2')
    assert 'Remove from faves'
    response = app.post('/fave?format=json', {'id':'t2', 'method':'delete'})
