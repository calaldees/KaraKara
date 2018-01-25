from pyramid.view import view_config

from . import action_ok, admin_only

#@view_config(route_name='admin_lock')
@admin_only
def admin_lock(request):
    request.registry.settings['admin_locked'] = not request.registry.settings.get('admin_locked', False)
    #log.debug('admin locked - {0}'.format(request.registry.settings['admin_locked']))
    request.log_event(admin_locked=request.registry.settings['admin_locked'])
    return action_ok()


#@view_config(route_name='admin_toggle')
def admin_toggle(request):
    if request.registry.settings.get('admin_locked'):
        raise action_error(message='additional admin users have been prohibited', code=403)
    request.session['admin'] = not request.session.get('admin', False)
    #log.debug('admin - {0} - {1}'.format(request.session['id'], request.session['admin']))
    request.log_event(admin=request.session['admin'])
    return action_ok()
