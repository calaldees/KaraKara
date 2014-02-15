from bs4 import BeautifulSoup

from externals.lib.misc import substring_in


def test_static(app):
    # Extract list of externals from homepage
    soup = BeautifulSoup(app.get('/').text)
    scripts = [script['src']  for script in soup.find_all('script')]
    links   = [link  ['href'] for link   in soup.find_all('link')  ]
    static_files = scripts + links
    
    # Request each external (no 404's should be found)
    for static_file in static_files:
        app.get(static_file)
    
    # Check we have all the known external files lists
    expected_externals = (
        'cssreset-min.css',
        'jquery.mobile.min.css',
        'main.css',
        'modernizer.custom.js',
        'jquery.min.js',
        'jquery.mobile-extras.js',
        'jquery.mobile.min.js',
        'jquery.cookie.js',
        'lib.js',
        'karakara.js',
        'favicon.ico',
    )
    for external in expected_externals:
        assert substring_in(external, static_files)
