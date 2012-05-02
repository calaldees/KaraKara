#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import pyramid.request
import pyramid.response

from decorator import decorator
import re
import copy

import logging
log = logging.getLogger(__name__)

from .pyramid_helpers import get_setting


#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

# Regex to extract 'format' from request URL
format_regex_path = re.compile(r'.*\.(?P<format>.*?)($|\?|#)'    , flags=re.IGNORECASE)
format_regex_qs   = re.compile(r'.*(^|,)format=(?P<format>.*?)($|,)', flags=re.IGNORECASE) # AllanC - this could be replaced at a later date when web_params_to_kwargs is implemented , used to use r'.*\?.*format=(.*?)($|,)' for whole url

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
    # Extract request object from args
    request = None
    for arg in args:
        if isinstance(arg, pyramid.request.Request):
            request = arg
            break
    assert request
    
    # Pre Processing -----------------------------------------------------------
    # None
    
    # Execute ------------------------------------------------------------------
    try:
        result = target(*args, **kwargs)
    except action_error:
        result = action_error.d
        log.warn("Auto format exception needs to be handled")
    
    # Post Processing ----------------------------------------------------------
    
    # Find format string 'format' based on input params, to then find a render func 'formatter'  - add potential formats in order of precidence
    formats = []
    # add kwarg 'format'
    try   : formats.append(kwargs['format'])
    except: pass
    # matched route 'format' key
    try   : formats.append(request.matchdict['format'])
    except: pass
    # add 'format' from URL path
    try   : formats.append(format_regex_path.match(request.path).group('format'))
    except: pass
    # add 'format' from URL query string
    try   : formats.append(format_regex_qs.match(request.path_qs).group('format'))
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
        # Add pending flash messages to result dict
        result['messages'] = result['messages'] + request.session.pop_flash()
        
        # Format result dict using format func
        response = formatter(request, result)
        
        # Set http response code
        if isinstance(response, pyramid.response.Response):
            response.status_int = result.get('code', 200)
        
        result = response
    
    return result

#-------------------------------------------------------------------------------
# Action Returns
#-------------------------------------------------------------------------------

def action_ok(message='', data={}, code=200, status='ok', **kwargs):
    assert isinstance(message, str)
    assert isinstance(data   , dict)
    assert isinstance(code   , int)
    d = {
        'status'  : status  ,
        'messages': [message],
        'data'    : data    ,
        'code'    : code    ,
    }
    d.update(kwargs)
    return d
    
class action_error(Exception):
    def __init__(self, message='', data={}, code=500, status='error', **kwargs):
        self.d = action_ok(message=message, data=data, code=code, status=status, **kwargs)
    def __str__( self ):
        return str(self.d)


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
    xml_head = '<?xml version="1.0" encoding="UTF-8"?>'.encode('utf-8')
    response = pyramid.response.Response(xml_head + dictToXMLString(result)) 
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

# Redirect---------------------------
from pyramid.httpexceptions import HTTPFound
def format_redirect(request, result):
    """
    A special case for compatable browsers making REST calls
    """
    # flash_message?
    # Placeholder - Untested!!! 
    return HTTPFound(location=request.referer)
