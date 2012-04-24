# Pyramid imports
from pyramid.config import Configurator
import pyramid.events

# SQLAlchemy imports
from sqlalchemy import engine_from_config
from .models import DBSession

# package imports
import karakara.subscribers as subscribers


def main(global_config, **settings):
    """
        This function returns a Pyramid WSGI application.
    """
    # Setup --------------------------------------------------------------------
    
    # Setup Db
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    
    # Setup Pyramid Global Settings
    config = Configurator(settings=settings)
    
    
    # Routes -------------------------------------------------------------------
    
    # Static Routes
    config.add_static_view('static', 'static', cache_max_age=3600)
    
    # Routes
    config.add_route('home'      , '/'          )
    config.add_route('helloworld', '/helloworld')
    
    
    # Events -------------------------------------------------------------------
    
    # Events
    # AllanC - These happen for every request, event for static content, sod it, why use the Pyramid framework, when a normal homegrown decorator is more understadable and manageable
    #config.add_subscriber(subscribers.handle_new_request , pyramid.events.NewRequest )
    #config.add_subscriber(subscribers.handle_new_response, pyramid.events.NewResponse)
    
    
    # Return -------------------------------------------------------------------
    config.scan()
    return config.make_wsgi_app()

