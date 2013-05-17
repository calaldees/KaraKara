__all__ = [
    "DBSession", "Base", "init_DBSession", "init_db", "commit"
    "JSONEncodedDict",
]

import logging
log = logging.getLogger(__name__)

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from sqlalchemy.orm             import scoped_session, sessionmaker
from zope.sqlalchemy            import ZopeTransactionExtension      # AllanC - Apparently, the recomended way to use Pyramid is with a transaction manager
DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))

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
    global engine
    log.info("Bind DBSession to engine")
    from sqlalchemy import engine_from_config
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)

#def init_DBSession(transactional=False):
    #connection = engine.connect()
    #if transactional:
    #    transaction = connection.begin()
    #return DBSession.configure(bind=connection), transaction
    #transaction.rollback() # can roll back with

def init_db():
    """
    Clears and Creates all DB tables associated with Base
    
    To be called AFTER init_DBSession
    """
    log.info("Drop all existing tables")
    Base.metadata.drop_all  (bind=DBSession.bind, checkfirst=True)
    log.info("Create all tables bound to Base")
    Base.metadata.create_all(bind=DBSession.bind                 ) #, checkfirst=True



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
import datetime

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

def to_dict(self, list_type='default', include_fields=None, exclude_fields=None, master_list_name='full', **kwargs):
    """
    Because API returns typiacally are dict objects, we need a convenient way to convert all DB objects to dicts
    
    list_type = empty | default | full
    """
    # Setup/Copy field list from exisintg list of fields -----------------------
    if list_type == 'empty':
        fields = {}
    else:
        if list_type not in self.__to_dict__:
            raise Exception("unsupported list type")
        fields = copy.copy(self.__to_dict__[list_type])
    
    # Import fields from include fields - if present ---------------------------
    try   : include_fields = [f.strip() for f in include_fields.split(',')]
    except: pass
    if isinstance(include_fields, list):
        for field in [field for field in include_fields if field in self.__to_dict__[master_list_name]]:
            fields[field] = self.__to_dict__[master_list_name][field]

    # Delete exlucded fields from return ---------------------------------------
    try   : exclude_fields = exclude_fields.split(',')
    except: pass
    if isinstance(exclude_fields, list):
        for field in [field for field in exclude_fields if field in fields]:
            del fields[field]

    return obj_to_dict(self, fields)


def to_dict_setup(self, list_type='default', clone_list='super', field_processors={}):
    """
    A failed experiment
    """
    if clone_list == 'super':
        self.__to_dict__ = copy.deepcopy(self.__class__.__bases__[0].__to_dict__)
    elif clone_list:
        self.__to_dict__.update({list_type: copy.deepcopy(__to_dict__[clone_list])})
    else:
        pass
    self.__to_dict__[list_type].update(field_processors)


def augment_declarative_base(base_class):
    base_class.__to_dict__    =  {}
    base_class.to_dict        = to_dict
    base_class.to_dict_setup  = to_dict_setup

augment_declarative_base(Base)


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