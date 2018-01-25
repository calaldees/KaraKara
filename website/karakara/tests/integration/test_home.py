

def test_home(app):
    """
    Main Menu
    """
    response = app.get('/')
    assert response.status_code == 200
    assert 'html' in response.content_type
    for text in ['KaraKara', 'jquery.mobile', 'queue']:
        assert text in response.text
