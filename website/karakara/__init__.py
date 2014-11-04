import re
import operator

# Pyramid imports
import pyramid.events
from pyramid.config import Configurator
from pyramid.request import Request
from pyramid.scripts.pserve import add_file_callback
from pyramid.session import SignedCookieSessionFactory  # TODO: should needs to be replaced with an encrypted cookie or a hacker at an event may be able to intercept other users id's

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
    config = Configurator(settings=settings) #, autocommit=True

    # Register Aditional Includes ---------------------------------------------
    config.include('pyramid_mako')  # The mako.directories value is updated in the scan for addons. We trigger the import here to include the correct folders.

    # Reload on template change
    template_filenames = map(operator.attrgetter('absolute'), file_scan(config.registry.settings['mako.directories']))
    add_file_callback(lambda: template_filenames)

    # Parse/Convert setting keys that have specifyed datatypes
    for key in config.registry.settings.keys():
        config.registry.settings[key] = convert_str_with_type(config.registry.settings[key])

    # Session Manager
    session_settings = extract_subkeys(config.registry.settings, 'session.')
    session_factory = SignedCookieSessionFactory(serializer=json_serializer, **session_settings)
    config.set_session_factory(session_factory)

    # Cachebust etags ----------------------------------------------------------
    #  crude implementation; count the number of tags in db, if thats changed, the etags will invalidate
    if not config.registry.settings['server.etag.cache_buster']:
        from .model.actions import rough_db_hash
        config.registry.settings['server.etag.cache_buster'] = rough_db_hash()

    # Search Config ------------------------------------------------------------
    import karakara.views.search
    karakara.views.search.search_config = read_json(config.registry.settings['karakara.search.view.config'])

    # WebSocket ----------------------------------------------------------------

    def authenicator(key):
        """Only admin authenticated keys can connect to the websocket"""
        request = Request({'HTTP_COOKIE':'{0}={1}'.format(config.registry.settings['session.cookie_name'],key)})
        session_data = session_factory(request)
        return session_data and session_data.get('admin')
    socket_manager = AuthEchoServerManager(
        authenticator=authenicator,
        websocket_port=config.registry.settings['karakara.websocket.port'],
        tcp_port      =config.registry.settings.get('karakara.tcp.port'),
    )
    config.registry['socket_manager'] = socket_manager
    socket_manager.start()

    # Login Providers ----------------------------------------------------------

    from .views.comunity_login import social_login
    social_login.user_store = ComunityUserStore()
    # Facebook
    if config.registry.settings.get('facebook.secret'):
        social_login.add_login_provider(FacebookLogin(
            appid=config.registry.settings.get('facebook.appid'),
            secret=config.registry.settings.get('facebook.secret'),
            permissions=config.registry.settings.get('facebook.permissions'),
        ))
    # Firefox Persona
    if config.registry.settings.get('persona.secret'):
        social_login.add_login_provider(PersonaLogin(site_url=config.registry.settings.get('server.url')))
    # No login provider
    elif config.registry.settings.get('karakara.server.mode') == 'development':
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
    config.add_static_view(name='player', path='karakara:{0}'.format(settings["static.player"]))

    # AllanC - it's official ... static route setup and generation is a mess in pyramid
    #config.add_static_view(name=settings["static.media" ], path="karakara:media" )
    config.add_static_view(name='files' , path=settings["static.media"])

    # Routes
    def append_format_pattern(route):
        return re.sub(r'{(.*)}', r'{\1:[^/\.]+}', route) + r'{spacer:[.]?}{format:(%s)?}' % '|'.join(registered_formats())

    config.add_route('home'          , append_format_pattern('/')              )
    config.add_route('track'         , append_format_pattern('/track/{id}')    )
    config.add_route('track_list'    , append_format_pattern('/track_list')    )
    config.add_route('queue'         , append_format_pattern('/queue')         )
    config.add_route('fave'          , append_format_pattern('/fave')          )
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

    config.add_route('search_tags'   , '/search_tags/{tags:.*}')
    config.add_route('search_list'   , '/search_list/{tags:.*}')

    # Upload extras -----
    config.add_route('upload', '/upload{sep:/?}{name:.*}')
    #config.add_route(settings['upload.route.uploaded'], path=settings['upload.route.uploaded'])
    config.add_static_view(name=settings['upload.route.uploaded'], path=settings['upload.path'])

    # Events -------------------------------------------------------------------
    config.add_subscriber(add_template_helpers_to_event, pyramid.events.BeforeRender)

    # Return -------------------------------------------------------------------
    config.scan(ignore='.tests')
    config.scan('externals.lib.pyramid_helpers.views')
    return config.make_wsgi_app()


def add_template_helpers_to_event(event):
    event['h'] = template_helpers
