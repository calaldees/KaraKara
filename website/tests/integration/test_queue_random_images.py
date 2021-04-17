

def test_random_images(app, queue, tracks):
    images = app.get(f'/queue/{queue}/random_images.json?count=200').json['data']['images']
    assert set(images) >= {'test/image1.jpg', 'test/image2.jpg', 'test/image3.png'}
