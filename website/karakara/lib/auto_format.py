import pyramid.request

from decorator import decorator
import re

import logging
log = logging.getLogger(__name__)

from .pyramid_helpers import get_setting


# Regex to extract 'format' from request URL
format_regex_path = re.compile(r'.*\.(.*?)($|\?|#)'      , flags=re.IGNORECASE)
format_regex_qs   = re.compile(r'.*\?.*format=(.*?)($|,)', flags=re.IGNORECASE)



auto_formaters = {}
def register_formater(format_name, format_func):
    """
    Register a format processor with a key
    e.g
    register_formater('json', dict_to_json_response_func)
    
    the format func could look up templates or call other libs to process the return
    
    format_funcs should return a Pyramid Response object
    """
    assert isinstance(format_name, str )
    assert isinstance(format_func, func)
    auto_formaters[format] = format_func


@decorator
def auto_format_output(target, *args, **kwargs):
    """
    A decorator to decarate a Pyramid view
    
    The view could return a plain python dict
    
    it will try to:
     - extract a sutable format string from the URL e.g html,json,xml,pdf,rss,etc
     - apply a format function to the plain python dict return
    
    """
    request = args[0]
    assert isinstance(request, pyramid.request.Request)
    
    # Pre Processing -----------------------------------------------------------
    
    # Get 'format' from URL path or query string
    format = get_setting('auto_format.default', request) or 'html'
    try   : format = format_regex_path.match(request.path).group(1)
    except: pass
    try   : format = format_regex_qs.match(request.path_qs).group(1)
    except: pass
    log.debug('Format=%s' % format)
    
    # Execute ------------------------------------------------------------------
    result = target(*args, **kwargs) 
    
    # Post Processing ----------------------------------------------------------
    
    # Attempt auto_format if result is a plain python dict and auto_format func exisits
    if isinstance(result, dict) and format in auto_formaters:
        log.debug('Applying %s formater' % format)
        result = auto_formaters[format](result)
    
    return result
