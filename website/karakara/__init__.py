# Pyramid imports
from pyramid.config import Configurator
import pyramid.events


# SQLAlchemy imports
from .model import DBSession, init_DBSession

# Beaker Sessions
import pyramid_beaker

# Other imports
import re

# Package Imports
from .lib.misc import convert_str_with_type
from .lib.auto_format import registered_formats
from .templates import helpers as template_helpers


def main(global_config, **settings):
    """
        This function returns a Pyramid WSGI application.
    """
    # Setup --------------------------------------------------------------------
    
    # Db
    init_DBSession(settings)
    
    # Pyramid Global Settings
    config = Configurator(settings=settings) #, autocommit=True
    
    # Beaker Session Manager
    config.set_session_factory(pyramid_beaker.session_factory_from_settings(settings))
    
    # Parse/Convert setting keys that have specifyed datatypes
    for key in config.registry.settings.keys():
        config.registry.settings[key] = convert_str_with_type(config.registry.settings[key])
    
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
    config.add_route('feedback'      , append_format_pattern('/feedback')      )
    config.add_route('settings'      , append_format_pattern('/settings')      )
    
    config.add_route('search_tags'   , '/search_tags/{tags:.*}')
    config.add_route('search_list'   , '/search_list/{tags:.*}')
    
    # Events -------------------------------------------------------------------
    config.add_subscriber(add_template_helpers_to_event, pyramid.events.BeforeRender)
    
    # Return -------------------------------------------------------------------
    config.scan(ignore='.tests')
    return config.make_wsgi_app()


def add_template_helpers_to_event(event):
    event['h'] = template_helpers

    