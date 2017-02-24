import json
import urllib.request
import re

BADGENAME_REGEX = re.compile(r'(?P<name>.*)\((?P<badge_name>.+)\)')
url = 'http://minamicon.org.uk/php/members-list-api.php'

webURL = urllib.request.urlopen(url)
raw_data = webURL.read()
encoding = webURL.info().get_content_charset('utf-8')
data = json.loads(raw_data.decode(encoding))

def get_badgename(name_string):
    return BADGENAME_REGEX.match(name_string).groupdict().get('badge_name')

for badgename in (get_badgename(member_dict.get('name')) for member_dict in data):
    print(badgename)
