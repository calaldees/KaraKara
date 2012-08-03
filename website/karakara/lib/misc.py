import re
import random
import datetime

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


def substring_in(substrings, string_list, ignore_case=True):
    """
    Find a substrings in a list of string_list
    Think of it as
      is 'bc' in ['abc', 'def']
    
    >>> substring_in( 'bc'      , ['abc','def','ghi'])
    True
    >>> substring_in( 'jkl'     , ['abc','def','ghi'])
    False
    >>> substring_in(['zx','hi'], ['abc','def','ghi'])
    True
    >>> substring_in(['zx','yw'], ['abc','def','ghi'])
    False
    """
    if not string_list or not substrings:
        return False
    if isinstance(substrings, str):
        substrings = [substrings]
    if not hasattr(string_list, '__iter__') or not hasattr(substrings, '__iter__'):
        raise TypeError('params mustbe iterable')
    for s in string_list:
        if not s:
            continue
        if ignore_case:
            s = s.lower()
        for ss in substrings:
            if ignore_case:
                ss = ss.lower()
            if ss in s:
                return True
    return False

def normalize_datetime(d, accuracy='hour'):
    """
    Normalizez datetime down to hour or day
    Dates are immutable (thank god)
    """
    if   accuracy=='hour':
        return d.replace(minute=0, second=0, microsecond=0)
    elif accuracy=='day' :
        return d.replace(minute=0, second=0, microsecond=0, hour=0)
    elif accuracy=='week':
        return d.replace(minute=0, second=0, microsecond=0, hour=0) - datetime.timedelta(days=d.weekday())
    return d

def is_base_types(d):
    """
    Recursively steps though a python dictionary
    Identifies strings and removes/replaces harmful/unwanted characters + collapses white space
    """
    #if isinstance(d, basestring):
    #    d = re.sub("'"   , "`", d)
    #    d = re.sub("\n"  , " ", d)
    #    d = re.sub(r"\s+", " ", d)
    #    d = d.strip()
    if hasattr(d, 'items'):
        for key, value in d.items():
            d[key] = is_base_types(value)
    elif hasattr(d,'__iter__'):
        for value in d:
            is_base_types(value)
    
    
    return d
