from pyramid.view import view_config

from . import web, action_ok, action_error, etag_decorator, generate_cache_key

import logging
log = logging.getLogger(__name__)


def generate_cache_key_homepage(request):
    """
    Custom etag for homepage
    The homepage template has a few if statements to display various buttons
    The buttons can be disables in settings.
    This custom etag takes all 'if' statements in the homepage template
    """
    return '-'.join((
        generate_cache_key(request),
        str(request.registry.settings.get('karakara.template.menu.disable')),
        str(bool(request.session.get('faves', [])) and request.registry.settings.get('karakara.faves.enabled')),
    ))


@view_config(context='karakara.traversal.QueueContext')
@etag_decorator(generate_cache_key_homepage)
@web
def queue_home(request):
    return action_ok()
