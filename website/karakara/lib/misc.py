import re
import random

def get_fileext(filename):
    try:
        return re.search(r'\.([^\.]+)$', filename).group(1).lower()
    except:
        return None
    

def update_dict(dict_a, dict_b):
    """
    Because dict.update(d) does not return the new dict
    
    Updates dict_a with the contents of dict_b

    >>> a = {'a': 1, 'b': 2}
    >>> update_dict(a, {'b': 3, 'c': 3})
    {'a': 1, 'c': 3, 'b': 3}
    """
    dict_a.update(dict_b)
    return dict_a


def random_string(length=8):
    """
    Generate a random string of a-z A-Z 0-9
    (Without vowels to stop bad words from being generated!)

    >>> len(random_string())
    8
    >>> len(random_string(10))
    10

    If random, it should compress pretty badly:

    >>> import zlib
    >>> len(zlib.compress(random_string(100))) > 50
    True
    """
    random_symbols = '1234567890bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ'
    r = ''
    for i in range(length):
        r += random_symbols[random.randint(0,len(random_symbols)-1)]
    return r
