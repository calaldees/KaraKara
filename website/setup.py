import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
#README = open(os.path.join(here, 'README.md')).read()


setup(
    name='KaraKara',
    version='0.1',
    description='KaraKara: Karaoke Event System - Attendees can view and queue tracks from their mobile phones',
    #long_description=README,
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
    keywords='web wsgi pyramid karaoke video',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='py.test',
    #tests_require=test_requires,
    #install_requires=install_requires + test_requires,
    entry_points="""\
    [paste.app_factory]
    main = karakara:main
    [console_scripts]
    populate_KaraKara = karakara.model.setup:main
    """,
)
