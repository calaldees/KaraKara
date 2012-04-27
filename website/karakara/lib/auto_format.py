#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import pyramid.request
import pyramid.response

from decorator import decorator
import re

import logging
log = logging.getLogger(__name__)

from .pyramid_helpers import get_setting


#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

# Regex to extract 'format' from request URL
format_regex_path = re.compile(r'.*\.(.*?)($|\?|#)'      , flags=re.IGNORECASE)
format_regex_qs   = re.compile(r'.*\?.*format=(.*?)($|,)', flags=re.IGNORECASE) # AllanC - this could be replaced at a later date when web_params_to_kwargs is implemented

#-------------------------------------------------------------------------------
# Setup
#-------------------------------------------------------------------------------

_auto_formaters = {}
def register_formater(format_name, format_func):
    """
    Register a format processor with a key
    e.g
    register_formater('json', dict_to_json_response_func)
    
    the format func could look up templates or call other libs to process the return
    
    format_funcs should return a Pyramid Response object
    """
    assert isinstance(format_name, str )
    assert callable(format_func)
    _auto_formaters[format_name] = format_func

#-------------------------------------------------------------------------------
# Decorator
#-------------------------------------------------------------------------------

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
    #  None
    
    # Execute ------------------------------------------------------------------
    result = target(*args, **kwargs) 
    
    # Post Processing ----------------------------------------------------------
    
    # Find format string 'format' based on input params, to then find a render func 'formatter'  - add potential formats in order of precidence
    formats = []
    # add kwarg 'format'
    try   : formats.append(kwargs['format'])
    except: pass
    # add 'format' from URL path
    try   : formats.append(format_regex_path.match(request.path).group(1))
    except: pass
    # add 'format' from URL query string
    try   : formats.append(format_regex_qs.match(request.path_qs).group(1))
    except: pass
    # add default format
    formats.append(get_setting('auto_format.default', request) or 'html')
    
    formatter = None
    for format in formats:
        try:
            formatter = _auto_formaters[format]
            log.debug('render format = %s' % format)
            break
        except:
            pass
    
    # Attempt auto_format if result is a plain python dict and auto_format func exisits
    if formatter and isinstance(result, dict):
        result = formatter(request, result)
    
    return result

#-------------------------------------------------------------------------------
# Renderer Template
#-------------------------------------------------------------------------------
from pyramid.renderers import render_to_response
import os.path
import copy

def render_template(request, result, format, template_data_param='d'):
    template_params = {template_data_param:result}
    template_params.update(request.matchdict)
    response = render_to_response(
        '%s.mako' % (os.path.join(format,request.matched_route.name)), 
        template_params,
        request=request,
    )
    return response

#-------------------------------------------------------------------------------
# Formatters
#-------------------------------------------------------------------------------

# Python dict formater -------------
register_formater('python', lambda result:result)

# JSON -----------------------------
import json
def format_json(request, result):
    response = pyramid.response.Response(json.dumps(result))
    response.headers['Content-type'] = "application/json; charset=utf-8"
    return response
register_formater('json', format_json)

# XML -------------------------------
from .xml import dictToXMLString
def format_xml(request, result):
    response = pyramid.response.Response('<?xml version="1.0" encoding="UTF-8"?>' + dictToXMLString(result))
    response.headers['Content-type'] = "text/xml; charset=utf-8"
    return response
register_formater('xml', format_xml)

# RSS -------------------------------
def format_rss(request, result):
    response = render_template(request, result, 'rss')
    response.headers['Content-type'] = "application/rss+xml; charset=utf-8"
    return response
register_formater('rss', format_rss)

# HTML ------------------------------
def format_html(request, result):
    response = render_template(request, result, 'html')
    return response
register_formater('html', format_html)