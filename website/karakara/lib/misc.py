import re

def get_fileext(filename):
    return re.search(r'\.([^\.]+)$', filename).group(1).lower()
    

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


