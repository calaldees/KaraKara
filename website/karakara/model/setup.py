from . import DBSession, init_DBSession

# AllanC - can anyone help move this into model.__init__
#          I want all generic stuff to be in __init__.py so the rest of the files in the model relate specificly to the project
#          when in __init__.py - the DBSession does not setup and engine properly. I'm assuming __init__ needs to finsh??

#-------------------------------------------------------------------------------
# Constants
#-------------------------------------------------------------------------------

version = "0.0"


#-------------------------------------------------------------------------------
# Command Line
#-------------------------------------------------------------------------------

def get_args():
    import argparse
    # Command line argument handling
    parser = argparse.ArgumentParser(
        description="""Init database""",
        epilog=""""""
    )
    parser.add_argument('--version'   , action='version', version=version)
    parser.add_argument('--config_uri', default='development.ini', help='config .ini uri')
    parser.add_argument('--init_func' , help='e.g. myapp.model.init_data:init_data')

    return parser.parse_args()

def main():
    args = get_args()
    
    # Setup Logging and import Settings
    from pyramid.paster import get_appsettings, setup_logging
    setup_logging(args.config_uri)
    settings = get_appsettings(args.config_uri)
    
    # Setup DB
    init_DBSession(settings) # Connect to DBSession

    def my_import(name):
        mod = __import__(name)
        components = name.split('.')
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod
    module_name, func_name = tuple(args.init_func.split(':'))
    init_func = getattr(my_import(module_name), func_name)
    #from .init_data import init_data as init_func
    init_func()
    
if __name__ == "__main__":
    main()    