

def test_feedback(app):
    
    # Check initial feedback form
    response = app.get('/feedback')
    for text in ['contact', 'details','email']:
        assert text in response.text
    assert 'readonly' not in response.text
    
    # Post feedback
    response = app.post('/feedback', {'contact':'test@test.com', 'details':'test feedback comment'})
    # Check details recived
    for text in ['test@test.com', 'test feedback comment', 'readonly']:
        assert text in response.text
    
    # Check get dose not give average user any data back
    response = app.get('/feedback')
    assert 'test@test.com' not in response.text
    
    # Check admin view
    response = app.get('/admin')
    response = app.get('/feedback')
    assert 'test@test.com' in response.text
    response = app.get('/admin')
