import os
import requests
from bs4 import BeautifulSoup
import re


import logging
log = logging.getLogger(__name__)

VERSION = '0.0'
DEFAULT_CACHE_FILENAME = 'badgenames.cache.html'


# Processors -------------------------------------------------------------------

def minami_processor(soup):
    """
    """
    regex = re.compile(r'(?P<name>.*)\((?P<badge_name>.*)\)')
    return [regex.match(name_string).groupdict()['badge_name'] for name_string in (cell.string for cell in soup.find_all('td')) if regex.match(name_string)]
minami_processor.url = "http://minamicon.org.uk/members.php"


def ame_processor(soup):
    """
    """
    import pdb ; pdb.set_trace()
    return []
ame_processor.url = "http://www.amecon.org.uk/registration/members"

processors = {
    'ame': ame_processor,
    'minami': minami_processor
}


# Comamnd Line -----------------------------------------------------------------

def get_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="""
        Import badge names for event
        """,
        epilog=""" """
    )

    parser.add_argument('-s', '--source', action='store', help='', choices=processors.keys())

    parser.add_argument('-v', '--verbose', action='store_true', help='', default=False)
    parser.add_argument('--version', action='version', version=VERSION)

    args = vars(parser.parse_args())
    return args


# Main -------------------------------------------------------------------------

def main():
    args = get_args()
    logging.basicConfig(level=logging.DEBUG if args['verbose'] else logging.INFO)

    processor = processors[args['source']]

    response_text = ''
    if os.path.exists(DEFAULT_CACHE_FILENAME):
        with open(DEFAULT_CACHE_FILENAME, 'r') as f:
            response_text = f.read()
    else:
        response_text = requests.get(processor.url).text
        if not os.path.exists(DEFAULT_CACHE_FILENAME):
            with open(DEFAULT_CACHE_FILENAME, 'w') as f:
                f.write(response_text)

    soup = BeautifulSoup(response_text)

    badge_names = processor(soup)

    for badge_name in badge_names:
        print(badge_name)
    #import pdb ; pdb.set_trace()
    #for name_string in (cell.string for cell in soup.find_all('td')):
    #    match = REGEX_NAME.match(name_string).groupdict()
    #    if match:
    #        match.groupdict()['badge_name']
    #assert 'jane' in BeautifulSoup(response.text).find(**{'class': 'flash_message'}).text.lower()


if __name__ == "__main__":
    main()
