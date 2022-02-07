__all__ = [
    "DBSession", "Base", "init_DBSession", "init_DBSession_tables", "clear_DBSession_tables", "commit"
    "JSONEncodedDict",
]
from typing import Dict, Any

import logging
log = logging.getLogger(__name__)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import scoped_session, sessionmaker
DBSession = scoped_session(sessionmaker(autoflush=False))

# Apparently, with Pyramid we need to use a transaction manager
from zope.sqlalchemy import register
register(DBSession)


engine = None


#-------------------------------------------------------------------------------
# DB Setup
#-------------------------------------------------------------------------------

def init_DBSession(settings):
    """
    To be called from Pyramid __init__ to setup SQLA from settings
    This binds inits DBSession and Base

    To be called AFTER all extentisons to Base have been imported/setup
    Import the files with your datamodel, before calling this.
    Upon this call is the SQLa tables are build/linked
    """
    import re

    # Make path to sqlite file if required
    sqlite_url_match = re.match(r'sqlite:///(?P<path>.*)', settings['sqlalchemy.url'])
    if sqlite_url_match:
        import os
        from pathlib import Path
        folder_database = Path(sqlite_url_match.group('path')).parent
        os.makedirs(folder_database, exist_ok=True)

    # Wait (a short period) for postgres port to open if needed
    postgres_url_match = re.match(r'postgres.*@(?P<host>.*?)\W', settings['sqlalchemy.url'])  # TODO: this is incomplete and wont identify an alternate port
    if postgres_url_match:
        import socket
        from calaldees.wait_for import wait_for
        TIMEOUT = 10
        socket_host_port_tuple = (postgres_url_match.group('host'), 5432)
        log.info(f'Waiting for postgresql socket to open at {socket_host_port_tuple} for {TIMEOUT} seconds')
        wait_for(
            func_attempt=lambda: socket.create_connection(socket_host_port_tuple, timeout=1),
            timeout=TIMEOUT,
            ignore_exceptions=True,
        )

    global engine
    from sqlalchemy import engine_from_config
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

#def init_DBSession(transactional=False):
    #connection = engine.connect()
    #if transactional:
    #    transaction = connection.begin()
    #return DBSession.configure(bind=connection), transaction
    #transaction.rollback() # can roll back with

def init_DBSession_tables():
    """
    Clears and Creates all DB tables associated with Base

    To be called AFTER init_DBSession
    """
    log.info("Create all tables (if needed) that are bound to DeclarativeBase")
    Base.metadata.create_all(bind=DBSession.bind, checkfirst=True)
    # after_create events are buggered - the tables are not created and stuck in the transaction manager - attempt to do this manually
    from karakara.model.init_data import init_initial_tags
    init_initial_tags()

def clear_DBSession_tables():
    log.info("Drop all tables that are bound to DeclarativeBase")
    Base.metadata.drop_all(bind=DBSession.bind, checkfirst=True)


#-------------------------------------------------------------------------------
# Extra DB Types
#-------------------------------------------------------------------------------

from sqlalchemy.types import TypeDecorator, VARCHAR
import json

class JSONEncodedDict(TypeDecorator):
    "Represents an immutable structure as a json-encoded string."

    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value



#-------------------------------------------------------------------------------
# Base Extensions
#-------------------------------------------------------------------------------

import copy

def obj_to_dict(obj, field_processors):
    """
    """
    d = {}
    for field_name, field_processor in field_processors.items():
        field_value = None
        # Get value ------------------------------------------------------------
        if not field_processor:         # No processor - just get value
            field_value = getattr(obj,field_name,'')
        elif callable(field_processor): # or involke processor (if present)
            field_value = field_processor(obj)
            
        # Convert value from known types ---------------------------------------
        if field_value:
            field_value_type = type(field_value)
            if hasattr(field_value,'keys') or hasattr(field_value, '__iter__'): # is a dict or list (could be done better)
                pass
            elif field_value_type in [int, float, bool]:
                pass
            #elif isinstance(field_value, datetime.datetime):
            #    field_value = field_value.strftime("%Y-%m-%d %H:%M:%S")
            #else:
            #    try   : field_value = str(field_value)
            #    except: raise Exception('Object types are not allowed in object dictionaries [%s]' % (field_name, ))

        d[field_name] = field_value
    return d


class CustomBase:
    __to_dict__: Dict[str, Dict[str, Any]] = {}

    def to_dict(self, list_type='default', include_fields=None, exclude_fields=None, master_list_name='full', **kwargs):
        """
        Because API returns typically are dict objects, we need a convenient way to convert all DB objects to dicts

        list_type = empty | default | full

        TODO: Doctest ...
        """
        # Setup/Copy field list from exisintg list of fields -----------------------
        if list_type == 'empty':
            fields = {}
        else:
            if list_type not in self.__to_dict__:
                raise Exception("unsupported list type")
            fields = copy.copy(self.__to_dict__[list_type])

        # Import fields from include fields - if present ---------------------------
        if isinstance(include_fields, str):
            include_fields = (f.strip() for f in include_fields.split(','))
        include_fields = tuple(include_fields) if include_fields else ()
        for field in [field for field in include_fields if field in self.__to_dict__[master_list_name]]:
            fields[field] = self.__to_dict__[master_list_name][field]

        # Delete excluded fields from return ---------------------------------------
        if isinstance(exclude_fields, str):
            exclude_fields = (f.strip() for f in exclude_fields.split(','))
        exclude_fields = tuple(exclude_fields) if exclude_fields else ()
        if exclude_fields:
            for field in [field for field in exclude_fields if field in fields]:
                del fields[field]

        return obj_to_dict(self, fields)

Base = declarative_base(cls=CustomBase)


#-------------------------------------------------------------------------------
# Commit
#-------------------------------------------------------------------------------

import transaction

def commit():
    """
    Commits the db session regardless of if it was setup with the zope transaction manager
    """
    try:
        DBSession.commit()
    except AssertionError as ae:
        transaction.commit()