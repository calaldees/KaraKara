from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import scoped_session, sessionmaker
from zope.sqlalchemy            import ZopeTransactionExtension

import logging
log = logging.getLogger(__name__)

__all__ = [
    "DBSession", "Base", "init_DBSession", "init_db",
]

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension())) # auto transaction commit after every request
Base      = declarative_base()

def init_DBSession(settings):
    """
    To be called from Pyramid __init__ to setup SQLA from settings
    This binds inits DBSession and Base
    
    To be called AFTER all extentisons to Base have been imported/setup
    """
    log.info("Bind DBSession to engine")
    from sqlalchemy import engine_from_config
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

def init_db():
    """
    Clears and Creates all DB tables associated with Base
    
    To be called AFTER init_DBSession
    """
    log.info("Drop all existing tables")
    Base.metadata.drop_all  (bind=DBSession.bind, checkfirst=True)
    log.info("Create all tables bound to Base")
    Base.metadata.create_all(bind=DBSession.bind                 ) #, checkfirst=True
