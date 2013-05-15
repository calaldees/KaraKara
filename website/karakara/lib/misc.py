import re
import random
import datetime

from pyramid.settings import asbool

# TODO - @property to get/set now?
_now_override = None
def now(new_override=None):
    global _now_override
    if new_override:
        _now_override = new_override
    if _now_override:
        return _now_override
    return datetime.datetime.now()


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

    # TODO (python3 needs a buffer here)
    #>>> import zlib
    #>>> len(zlib.compress(random_string(100))) > 50
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

def normalize_datetime(d=None, accuracy='hour'):
    """
    Normalizez datetime down to hour or day
    Dates are immutable (thank god)
    """
    if not d:
        d = datetime.datetime.now()
    if   accuracy=='hour':
        return d.replace(minute=0, second=0, microsecond=0)
    elif accuracy=='day' :
        return d.replace(minute=0, second=0, microsecond=0, hour=0)
    elif accuracy=='week':
        return d.replace(minute=0, second=0, microsecond=0, hour=0) - datetime.timedelta(days=d.weekday())
    return d

def parse_timedelta(text):
    """
    Takes string and converts to timedelta

    ##>>> parse_timedelta('00:01:00.01')
    ##datetime.timedelta(0, 60, 1)
    
    >>> parse_timedelta('00:00:01.00')
    datetime.timedelta(0, 1)
    >>> parse_timedelta('01:00:00')
    datetime.timedelta(0, 3600)
    >>> parse_timedelta('5')
    datetime.timedelta(0, 5)
    >>> parse_timedelta('1:01')
    datetime.timedelta(0, 3660)
    """
    hours = "0"
    minutes = "0"
    seconds = "0"
    milliseconds = "0"
    time_components = text.strip().split(':')
    if   len(time_components) == 1:
        seconds = time_components[0]
    elif len(time_components) == 2:
        hours = time_components[0]
        minutes = time_components[1]
    elif len(time_components) == 3:
        hours   = time_components[0]
        minutes = time_components[1]
        seconds = time_components[2]
    second_components = seconds.split('.')
    if len(second_components) == 2:
        seconds      = second_components[0]
        milliseconds = second_components[1]
    hours = int(hours)
    minutes = int(minutes)
    seconds = int(seconds)
    milliseconds = int(milliseconds)
    assert hours>=0
    assert minutes>=0
    assert seconds>=0
    assert milliseconds==0, 'milliseconds are not implemented properly .01 is parsed as int(01), this is incorrect, fix this!' 
    return datetime.timedelta(
        seconds      = seconds + minutes*60 + hours*60*60,
        milliseconds = milliseconds
    )


def strip_non_base_types(d):
    """
    Recursively steps though a python dictionary
    Identifies strings and removes/replaces harmful/unwanted characters + collapses white space
    
    (The tests below rely on the dict ordering in the output, if pythons dict ordering changes this will break)
    
    >>> strip_non_base_types('a')
    'a'
    >>> strip_non_base_types({'a':1, 'b':'2', 'c':[3,4,5], 'd':{'e':'6'}})
    {'a': 1, 'c': [3, 4, 5], 'b': '2', 'd': {'e': '6'}}
    >>> strip_non_base_types({'a':1, 'b':'2', 'c':[3,4,5], 'd':{'e':datetime.datetime.now()}})
    {'a': 1, 'c': [3, 4, 5], 'b': '2', 'd': {'e': None}}

    """
    for t in [str,int,float,bool]:
        if isinstance(d,t):
            return d
    if hasattr(d, 'items'):
        return {key:strip_non_base_types(value) for key, value in d.items()}
    for t in [list,set,tuple]:
        if isinstance(d,t):
            return [strip_non_base_types(value) for value in d]
    return None


def convert_str_with_type(value_string, value_split='->'):
    """
    >>> convert_str_with_type("5 -> int")
    5
    >>> convert_str_with_type("00:00:01 -> timedelta")
    datetime.timedelta(0, 1)
    """
    try:
        value, return_type = value_string.split(value_split)
        return convert_str(value.strip(), return_type.strip())
    except (ValueError, AttributeError) as e:
        return value_string

def convert_str(value, return_type):
    """
    >>> convert_str('bob', None)
    'bob'
    >>> convert_str('1', int)
    1
    >>> convert_str('yes', 'bool')
    True
    >>> convert_str('a,b ,c', 'list')
    ['a', 'b', 'c']
    """
    if not value or not isinstance(value, str) or not return_type:
        return value
    if return_type=='bool' or return_type==bool:
        return asbool(value)
    if return_type=='int' or return_type==int:
        return int(value)
    if return_type=='time' or return_type==datetime.time:
        return dateutil.parser.parse(value).time()
    if return_type=='date' or return_type==datetime.date:
        return dateutil.parser.parse(value).date()
    if return_type=='datetime' or return_type==datetime.datetime:
        return dateutil.parser.parse(value)
    if return_type=='timedelta' or return_type==datetime.timedelta:
        return parse_timedelta(value)
    if return_type=='list' or return_type==list:
        return [v.strip() for v in value.split(',') if v.strip()]
    assert False, 'unable to convert {0} to {1}'.format(value, return_type)
