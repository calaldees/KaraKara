from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


from . import web, action_ok, action_error, admin_only


import logging
log = logging.getLogger(__name__)


@view_config(context='karakara.traversal.TraversalGlobalRootFactory')
@web
def home(request):
    # Short term hack. Do not allow normal root page in commuity mode - redirect to comunity
    # Need to implement a proper pyramid authorize system when in comunity mode
    if request.registry.settings.get('karakara.server.mode') == 'comunity':
        raise HTTPFound(location='/comunity')
    return action_ok()


@view_config(route_name='stats')
@web
def stats(request):
    return action_ok()


@view_config(route_name='admin_lock')
@web
@admin_only
def admin_lock(request):
    request.registry.settings['admin_locked'] = not request.registry.settings.get('admin_locked', False)
    #log.debug('admin locked - {0}'.format(request.registry.settings['admin_locked']))
    request.log_event(admin_locked=request.registry.settings['admin_locked'])
    return action_ok()


@view_config(route_name='admin_toggle')
@web
def admin_toggle(request):
    if request.registry.settings.get('admin_locked'):
        raise action_error(message='additional admin users have been prohibited', code=403)
    request.session['admin'] = not request.session.get('admin', False)
    #log.debug('admin - {0} - {1}'.format(request.session['id'], request.session['admin']))
    request.log_event(admin=request.session['admin'])
    return action_ok()
