
def test_track_view(app, tracks):
    response = app.get('/track/t1')
    assert 'Test track 1' in response.text