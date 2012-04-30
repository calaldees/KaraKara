# Pyramid imports
from pyramid.config import Configurator
import pyramid.events

# SQLAlchemy imports
from .model.models import DBSession, init_DBSession

# Beaker Sessions
import pyramid_beaker

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
    
    
    # Routes -------------------------------------------------------------------
    
    # Static Routes
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    # Routes
    config.add_route('home'          , '/'              )
    
    
    config.add_route('track'         , '/track/{id}'    )
    #config.add_route('track'         , '/track/{id}.{format}')

    config.add_route('track_list'    , '/track_list'    )
    config.add_route('track_list_all', '/track_list_all')
    config.add_route('queue'         , '/queue'         )
    config.add_route('fave'          , '/fave'          )
    
    
    # Events -------------------------------------------------------------------
    
    
    # Return -------------------------------------------------------------------
    config.scan()
    return config.make_wsgi_app()

