from ..model import init_DBSession

import logging
from pyramid.paster import get_appsettings, setup_logging
#setup_logging(args.config_uri)
#logging.basicConfig(level=logging.INFO)
settings = get_appsettings('test.ini')
init_DBSession(settings)
