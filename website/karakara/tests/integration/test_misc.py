
def test_home(app):
    """
    Main Menu
    """
    response = app.get('/')
    assert response.status_code == 200
    assert 'html' in response.content_type
    for text in ['KaraKara', 'jquery-1.', 'jquery.mobile', 'Feedback', 'Explore']:
        assert text in response.text
    
def test_admin_toggle(app):
    """
    Swich to admin mode
    check main menu for admin options
    """
    assert not app.get('/?format=json').json['identity']['admin']
    
    response = app.get('/admin')
    assert 'admin' in response.text
    response = app.get('/')
    for text in ['Exit Admin Mode']:
        assert text in response.text
    response = app.get('/admin')
    
    assert not app.get('/?format=json').json['identity']['admin']

def test_admin_lock(app):
    """
    Test Admin Lock
    When multiple users have become admins. The system can be prevented from allowing more admins
    This saves the need to dick about with passwords.
    """
    assert not app.get('/?format=json').json['identity']['admin']
    
    response = app.get('/admin')
    response = app.get('/admin_lock')
    response = app.get('/admin', expect_errors=True)
    assert response.status_code == 403
    response = app.get('/admin_lock')
    response = app.get('/admin')
    
    assert not app.get('/?format=json').json['identity']['admin']

def test_settings(app):
    # Settings API
    settings = app.get('/settings.json').json['data']['settings']
    assert settings
    
    # Settings Template
    response = app.get('/settings')
    assert 'setting' in response.text
