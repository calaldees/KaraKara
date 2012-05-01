import re

def get_fileext(filename):
    return re.search(r'\.([^\.]+)$', filename).group(1).lower()