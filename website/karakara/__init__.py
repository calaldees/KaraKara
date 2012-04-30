# Pyramid imports
from pyramid.config import Configurator
import pyramid.events

# SQLAlchemy imports

from .model.models import DBSession, init_DBSession


def main(global_config, **settings):
    """
        This function returns a Pyramid WSGI application.
    """
    # Setup --------------------------------------------------------------------
    
    # Setup Db
    init_DBSession(settings)
    
    # Setup Pyramid Global Settings
    config = Configurator(settings=settings)
    
    
    # Routes -------------------------------------------------------------------
    
    # Static Routes
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    # Routes
    config.add_route('home'      , '/'          )
    config.add_route('track'     , '/track/{id}')
    
    
    # Events -------------------------------------------------------------------
    
    
    # Return -------------------------------------------------------------------
    config.scan()
    return config.make_wsgi_app()

