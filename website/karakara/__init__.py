import re
import operator

# Pyramid imports
import pyramid.events
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.scripts.pserve import add_file_callback
from pyramid.session import SignedCookieSessionFactory  # TODO: should needs to be replaced with an encrypted cookie or a hacker at an event may be able to intercept other users id's
from pyramid.i18n import get_localizer, TranslationStringFactory

# External Imports
from externals.lib.misc import convert_str_with_type, read_json, extract_subkeys, json_serializer, file_scan
from externals.lib.pyramid_helpers.auto_format import registered_formats
from externals.lib.social._login import NullLoginProvider, FacebookLogin, PersonaLogin
from externals.lib.multisocket.auth_echo_server import AuthEchoServerManager

# Package Imports
from .templates import helpers as template_helpers
from .auth import ComunityUserStore, NullComunityUserStore
# SQLAlchemy imports
from .model import init_DBSession

import logging
log = logging.getLogger(__name__)

translation_string_factory = TranslationStringFactory('karakara')

# HACK! - Monkeypatch Mako 0.8.1 - HACK!
#import mako.filters
#html_escape_mako = mako.filters.html_escape
#mako.filters.html_escape = lambda s: html_escape_mako(str(s) if not isinstance(s, str) else s)


def main(global_config, **settings):
    """
        This function returns a Pyramid WSGI application.
    """
    # Setup --------------------------------------------------------------------

    # Db
    init_DBSession(settings)

    # Pyramid Global Settings
    config = Configurator(settings=settings)  # , autocommit=True

    # Register Aditional Includes ---------------------------------------------
    config.include('pyramid_mako')  # The mako.directories value is updated in the scan for addons. We trigger the import here to include the correct folders.

    # Reload on template change
    template_filenames = map(operator.attrgetter('absolute'), file_scan(config.registry.settings['mako.directories']))
    add_file_callback(lambda: template_filenames)

    # Parse/Convert setting keys that have specifyed datatypes
    for key in config.registry.settings.keys():
        config.registry.settings[key] = convert_str_with_type(config.registry.settings[key])

    # i18n
    config.add_translation_dirs(config.registry.settings['i18n.translation_dirs'])

    # Session Manager
    session_settings = extract_subkeys(config.registry.settings, 'session.')
    session_factory = SignedCookieSessionFactory(serializer=json_serializer, **session_settings)
    config.set_session_factory(session_factory)

    # Cachebust etags ----------------------------------------------------------
    #  crude implementation; count the number of tags in db, if thats changed, the etags will invalidate
    if not config.registry.settings['server.etag.cache_buster']:
        from .model.actions import last_update
        config.registry.settings['server.etag.cache_buster'] = 'last_update:{0}'.format(str(last_update()))

    # Search Config ------------------------------------------------------------
    import karakara.views.search
    karakara.views.search.search_config = read_json(config.registry.settings['karakara.search.view.config'])

    # WebSocket ----------------------------------------------------------------

    class NullAuthEchoServerManager(object):
        def recv(self, *args, **kwargs):
            pass
    socket_manager = NullAuthEchoServerManager()

    # Do not activate websocket if in community mode
    if config.registry.settings.get('karakara.server.mode') == 'comunity':
        config.registry.settings['karakara.websocket.port'] = None

    if config.registry.settings.get('karakara.websocket.port'):
        def authenicator(key):
            """Only admin authenticated keys can connect to the websocket"""
            request = Request({'HTTP_COOKIE':'{0}={1}'.format(config.registry.settings['session.cookie_name'],key)})
            session_data = session_factory(request)
            return session_data and session_data.get('admin')
        try:
            _socket_manager = AuthEchoServerManager(
                authenticator=authenicator,
                websocket_port=config.registry.settings['karakara.websocket.port'],
                tcp_port=config.registry.settings.get('karakara.tcp.port'),
            )
            _socket_manager.start()
            socket_manager = _socket_manager
        except OSError:
            log.warn('Unable to setup websocket')

    config.registry['socket_manager'] = socket_manager


    # Login Providers ----------------------------------------------------------

    from .views.comunity_login import social_login
    social_login.user_store = ComunityUserStore()
    login_providers = config.registry.settings.get('login.provider.enabled')
    # Facebook
    if 'facebook' in login_providers:
        social_login.add_login_provider(FacebookLogin(
            appid=config.registry.settings.get('facebook.appid'),
            secret=config.registry.settings.get('facebook.secret'),
            permissions=config.registry.settings.get('facebook.permissions'),
        ))
    # Firefox Persona
    if 'persona' in login_providers:
        social_login.add_login_provider(PersonaLogin(site_url=config.registry.settings.get('server.url')))
    # No login provider
    if not login_providers and config.registry.settings.get('karakara.server.mode') == 'development':
        # Auto login if no service keys are provided
        social_login.add_login_provider(NullLoginProvider())
        social_login.user_store = NullComunityUserStore()
    template_helpers.javascript_inline['comunity'] = social_login.html_includes

    # Renderers ----------------------------------------------------------------

    # AllanC - currently the auto_format decorator does all the formatting work
    #          it would be far preferable to use the pyramid renderer framework
    #          issue is, we want to set the renderer to be dynamic based on the url given
    #          I don't want to define EVERY method with loads of renderer tags
    #          and I don't want to define 5+ routes for every view callable with differnt formats
    #          We need a nice way of doing this in pyramid, and right now, after HOURS of trawling
    #          the doc and experimenting, I cant find one.
    #from .renderers.auto_render_factory import AutoRendererFactory, handle_before_render
    #config.add_renderer(None   , AutoRendererFactory) #'renderers.auto_render_factory.auto_renderer_factory'
    #config.add_renderer('.html', 'pyramid.mako_templating.renderer_factory')
    #config.add_subscriber(handle_before_render , pyramid.events.BeforeRender) # maybe use this to set renderer?
    # closeset ive seen
    #   http://zhuoqiang.me/a/restful-pyramid
    #   http://stackoverflow.com/questions/4633320/is-there-a-better-way-to-switch-between-html-and-json-output-in-pyramid


    # Routes -------------------------------------------------------------------

    # Static Routes
    config.add_static_view(name='ext'   , path='../externals/static') #cache_max_age=3600 # settings["static.assets"]
    config.add_static_view(name='static', path='karakara:{0}'.format(settings["static.assets"])) #cache_max_age=3600 # settings["static.assets"]
    config.add_static_view(name='player', path=settings["static.player"])

    # AllanC - it's official ... static route setup and generation is a mess in pyramid
    #config.add_static_view(name=settings["static.media" ], path="karakara:media" )
    config.add_static_view(name='files' , path=settings["static.processed"])

    # Routes
    def append_format_pattern(route):
        return re.sub(r'{(.*)}', r'{\1:[^/\.]+}', route) + r'{spacer:[.]?}{format:(%s)?}' % '|'.join(registered_formats())

    config.add_route('home'          , append_format_pattern('/')              )
    config.add_route('track'         , append_format_pattern('/track/{id}')    )
    config.add_route('track_list'    , append_format_pattern('/track_list')    )
    config.add_route('queue'         , append_format_pattern('/queue')         )
    config.add_route('priority_tokens', append_format_pattern('/priority_tokens'))
    config.add_route('fave'          , append_format_pattern('/fave')          )
    config.add_route('message'       , append_format_pattern('/message')          )
    config.add_route('admin_toggle'  , append_format_pattern('/admin')         )
    config.add_route('admin_lock'    , append_format_pattern('/admin_lock')    )
    config.add_route('remote'        , append_format_pattern('/remote')        )
    config.add_route('feedback'      , append_format_pattern('/feedback')      )
    config.add_route('settings'      , append_format_pattern('/settings')      )
    config.add_route('random_images' , append_format_pattern('/random_images') )
    config.add_route('inject_testdata' , append_format_pattern('/inject_testdata') )
    config.add_route('stats'         , append_format_pattern('/stats')         )
    config.add_route('comunity'      , append_format_pattern('/comunity')      )
    config.add_route('comunity_login', append_format_pattern('/comunity/login'))
    config.add_route('comunity_logout', append_format_pattern('/comunity/logout'))
    config.add_route('comunity_list' , append_format_pattern('/comunity/list') )
    config.add_route('comunity_track', append_format_pattern('/comunity/track/{id}'))
    config.add_route('comunity_upload', append_format_pattern('/comunity/upload'))
    config.add_route('comunity_settings', append_format_pattern('/comunity/settings'))

    config.add_route('search_tags'   , '/search_tags/{tags:.*}')
    config.add_route('search_list'   , '/search_list/{tags:.*}')

    # Upload extras -----
    #config.add_static_view(name=settings['upload.route.uploaded'], path=settings['upload.path'])  # the 'upload' route above always matchs first
    config.add_route('upload', '/upload{sep:/?}{name:.*}')

    # Events -------------------------------------------------------------------
    config.add_subscriber(add_localizer_to_request, pyramid.events.NewRequest)
    config.add_subscriber(add_render_globals_to_template, pyramid.events.BeforeRender)

    # Return -------------------------------------------------------------------
    config.scan(ignore='.tests')
    config.scan('externals.lib.pyramid_helpers.views')
    return config.make_wsgi_app()


def add_localizer_to_request(event):
    request = event.request
    localizer = get_localizer(request)
    def auto_translate(*args, **kwargs):
        return localizer.translate(translation_string_factory(*args, **kwargs))
    request.localizer = localizer
    request.translate = auto_translate


def add_render_globals_to_template(event):
    request = event['request']
    event['_'] = request.translate
    event['localizer'] = request.localizer
    event['h'] = template_helpers
