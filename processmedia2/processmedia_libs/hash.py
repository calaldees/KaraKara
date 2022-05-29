import hashlib
import base64
import re
from collections.abc import Sequence

def gen_string_hash(hashs: Sequence[str]):
    """
    >>> gen_string_hash(('1', '2', '3'))
    'pmWkWSBCL51'
    """
    #if isinstance(hashs, str):
    #    return hashs

    hasher = hashlib.sha256()
    hasher.update(''.join(sorted(hashs)).encode('utf-8'))
    #hash_str = hasher.hexdigest()

    # Use base62 string rather than hex
    # re.sub('[+/=]','_', base64.b64encode(hashlib.sha256().digest()).decode('utf8'))[:11]
    # This is filesystem safe, but not bi-directional as some data is lost
    # pow(62, 11) == 52036560683837093888  # this is 4 times more-ish than int64 pow(2,64)
    # pow(62, 10) ==   839299365868340224
    return re.sub('[+/=]','_', base64.b64encode(hasher.digest()).decode('utf8'))[:11]
