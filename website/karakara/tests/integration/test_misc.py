
def test_home(app):
    """
    Main Menu    
    """
    response = app.get('/')
    assert response.status_code == 200
    assert 'html' in response.content_type
    for text in ['KaraKara', 'jquery-1.', 'jquery.mobile', 'Feedback', 'Explore']:
        assert text in response.text
        

def test_home_disabled(app):
    """
    Menu has - a lightweight menu message diabler:
    In the event of load affecting the presentation screen we want a
    lightweight way to diable the system and inform users.
    We still want the system to operate for admins.
    Rather than locking down everthing venomusly, we can just disable the main menu.
    This will inform most users and throttle most traffic.
    """
    response = app.put('/settings', {
        'karakara.template.menu.disable':'test menu disbaled',
    })

    response = app.get('/')
    assert 'test menu disbaled' in response.text
    
    response = app.get('/admin')
    response = app.get('/')
    assert 'test menu disbaled' not in response.text
    response = app.get('/admin')

    response = app.put('/settings', {
        'karakara.template.menu.disable':'',
    })

    response = app.get('/')
    assert 'test menu disbaled' not in response.text

    

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

def test_readonly_mode(app, tracks):
    response = app.get('/track/t1')
    assert "form action='/queue" in response.text
    
    response = app.put('/settings', {
        'karakara.system.user.readonly':'True -> bool',
    })

    # Normal users are restricted
    response = app.get('/track/t1')
    assert "form action='/queue" not in response.text

    response = app.post('/queue', dict(track_id='t1', performer_name='bob'), expect_errors=True)
    assert response.status_code==403
    assert 'readonly' in response.text
    
    # Admin users function as normal
    response = app.get('/admin')
    response = app.get('/track/t1')
    assert "form action='/queue" in response.text
    # TODO - we need a way of adding to the queue and getting the queue_item.id back in the response
    #        currently this is not possible as the commit happens at the transaction level automatically
    #response = app.post('/queue.json', dict(track_id='t1', performer_name='bob')).json['data']
    #assert False
    response = app.get('/admin')
    
    # TODO - test 'update' and 'delete'? - for now testing the decoration once (above) is light enough
    
    response = app.put('/settings', {
        'karakara.system.user.readonly':'False -> bool',
    })
    
    
    
