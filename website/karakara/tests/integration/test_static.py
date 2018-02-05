import bs4
def BeautifulSoup(markup):
    return bs4.BeautifulSoup(markup, "html.parser")


from externals.lib.misc import substring_in

from . import admin_rights


def test_static(app, queue):

    def external_links(path):
        """ Extract list of externals from page """
        soup = BeautifulSoup(app.get(path).text)
        scripts = {script['src'] for script in soup.find_all('script')}
        links = {link['href'] for link in soup.find_all('link')}
        return scripts | links

    static_files = set()
    with admin_rights(app, queue):
        for path in ('/', f'/queue/{queue}/track_list'):
            static_files |= external_links(path)

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
        'print_list.css',
    )
    for external in expected_externals:
        assert substring_in(external, static_files)
