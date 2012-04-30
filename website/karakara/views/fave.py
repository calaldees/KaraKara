from pyramid.view import view_config

from ..lib.auto_format    import auto_format_output


#-------------------------------------------------------------------------------
# Faves
#-------------------------------------------------------------------------------

@view_config(route_name='fave', request_method='GET')
@auto_format_output
def fave_view(request):
    """
    view current faves
    """
    return {}

@view_config(route_name='fave', request_method='POST')
@auto_format_output
def fave_add(request):
    """
    Add item to faves in session
    """
    return {}

@view_config(route_name='fave', request_method='DELETE')
@auto_format_output
def fave_del(request):
    """
    Remove fave from session
    """
    return {}
