import re

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from externals.lib.misc import convert_str_with_type

from . import web, action_ok, action_error, method_put_router, is_admin, is_comunity, admin_only, etag_decorator, generate_cache_key


import logging
log = logging.getLogger(__name__)

#-------------------------------------------------------------------------------
# Misc
#-------------------------------------------------------------------------------

def generate_cache_key_homepage(request):
    """
    Custom etag for homepage
    The homepage template has a few if statements to display various buttons
    The buttons can be disables in settings.
    This custom etag takes all 'if' statements in the homepage template    
    """
    return '-'.join((
        generate_cache_key(request),
        str(request.registry.settings.get('karakara.template.menu.disable')),
        str(bool(request.session.get('faves',[])) and request.registry.settings.get('karakara.faves.enabled')),
    ))

@view_config(route_name='home')
@etag_decorator(generate_cache_key_homepage)
@web
def home(request):
    # Short term hack. Do not allow normal root page in commuity mode - redirect to comunity
    # Need to implement a proper pyramid authorize system when in comunity mode
    if request.registry.settings['comunity.enabled']:
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
    request.registry.settings['admin_locked'] = not request.registry.settings.get('admin_locked',False)
    log.debug('admin locked - {0}'.format(request.registry.settings['admin_locked']))
    return action_ok()

@view_config(route_name='admin_toggle')
@web
def admin_toggle(request):
    if request.registry.settings.get('admin_locked'):
        raise action_error(message='additional admin users have been prohibited', code=403)
    request.session['admin'] = not request.session.get('admin',False)
    log.debug('admin - {0} - {1}'.format(request.session['id'], request.session['admin']))
    return action_ok()

@view_config(route_name='remote')
@web
@admin_only
def remote(request):
    cmd = request.params.get('cmd')
    if cmd:
        log.debug("remote command - {0}".format(cmd))
        request.registry['socket_manager'].recv(cmd.encode('utf-8'))
    return action_ok()

@view_config(route_name='settings')
@web
def settings(request):
    """
    Surface settings as an API.
    This allows clients to qurey server settup rather than having to hard code bits into the clients
    """
    if not is_admin(request):
        log.debug('settings requested by non admin')  # I'm curious if anyone will find this. would be fun to search logs after an event for this string
    
    if method_put_router(None, request):
        # with PUT requests, update settings
        #  only changing in production is bit over zelious #request.registry.settings.get('karakara.server.mode')!='production'
        if request.registry.settings.get('karakara.server.mode')!='test' and not is_admin(request):
            raise action_error(message='Settings modification for non admin users forbidden', code=403)
        
        for key, value in request.params.items():
            fallback_type = None
            if request.registry.settings.get(key) != None:
                fallback_type = type(request.registry.settings.get(key))
            request.registry.settings[key] = convert_str_with_type(value, fallback_type=fallback_type)
    
    setting_regex = re.compile(request.registry.settings.get('api.settings.regex','TODOmatch_nothing_regex'))
    return action_ok(
        data={
            'settings': {
                setting_key:request.registry.settings.get(setting_key)
                for setting_key in
                [key for key in request.registry.settings.keys() if setting_regex.match(key)]
            }
        }
    )

@view_config(route_name='random_images')
@web
def random_images(request):
    """
    The player interface titlescreen can be populated with random thumbnails from the system.
    This is a nice showcase.
    Not optimised as this is rarely called.
    """
    import random
    from karakara.model              import DBSession
    from karakara.model.model_tracks import Attachment
    thumbnails = DBSession.query(Attachment.location).filter(Attachment.type=='thumbnail').all()
    random.shuffle(thumbnails)
    thumbnails = [t[0] for t in thumbnails]
    return action_ok(data={'thumbnails':thumbnails[0:int(request.params.get('count',0) or 100)]})
