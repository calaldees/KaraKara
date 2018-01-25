from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound


from . import web, action_ok, action_error, admin_only


import logging
log = logging.getLogger(__name__)


@view_config(
    context='karakara.traversal.RandomImagesContext',
)
def random_images(request):
    """
    The player interface titlescreen can be populated with random thumbnails from the system.
    This is a nice showcase.
    Not optimised as this is rarely called.
    """
    import random
    from karakara.model import DBSession
    from karakara.model.model_tracks import Attachment
    images = DBSession.query(Attachment.location).filter(Attachment.type == 'image').all()
    # TODO: use serach.restrict_trags to get the images for the current event
    random.shuffle(images)
    images = [t[0] for t in images]
    return action_ok(data={'images': images[0: int(request.params.get('count', 0) or 100)]})
