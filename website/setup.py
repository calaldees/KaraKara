import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

install_requires = [
    'pyramid',
    'SQLAlchemy',
    'transaction',
    'pyramid_tm',
    'pyramid_mako',
    'pyramid_debugtoolbar',
    'zope.sqlalchemy',
    'waitress',
    'decorator',
    'beautifulsoup4',  # Inspecting html/xml (used in db import crawling)
    'py-postgresql',  # any DB API should do, this one is pure python
    'python-dateutil',
    'dogpile.cache',
    'pycrypto',  # Considering this inclusion for encrypted cookies
    'python-magic',  # File upload mime type detection (requires libmagic1 c lib)
    'requests',
    'Babel',
    'httpagentparser',
    'humanize',
]
test_requires = [
    'pytest',
    'webtest',
]
# http://stackoverflow.com/questions/4734292/specifying-where-to-install-tests-require-dependecies-of-a-distribute-setuptoo


setup(
    name='KaraKara',
    version='0.1',
    description='KaraKara: Karaoke Event System - Attendees can view and queue tracks from their mobile phones',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='calaldees@gmail.com',
    url='http://github.com/calaldees/KaraKara',
    keywords='web wsgi bfg pylons pyramid jquery jquerymobile karaoke nginx html5 video',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='py.test',
    tests_require=test_requires,
    install_requires=install_requires + test_requires,
    entry_points="""\
    [paste.app_factory]
    main = karakara:main
    [console_scripts]
    populate_KaraKara = karakara.model.setup:main
    """,
    message_extractors={
        'karakara': [
            ('**.py'            , 'python', None),  # could replace None with {'input_encoding': 'utf-8'}
            ('templates/**.html', 'mako'  , None),
            ('templates/**.mako', 'mako'  , None),
            ('static/**'        , 'ignore', None),
        ]
    },
)
