from pyramid.view import view_config

import os
import random
from sqlalchemy.orm import joinedload

from ..model              import DBSession
from ..model.model_tracks import Track

from . import web, action_ok, cache, generate_cache_key


import logging
log = logging.getLogger(__name__)


#-------------------------------------------------------------------------------
# Cache Management
#-------------------------------------------------------------------------------
LIST_CACHE_KEY = 'comunity_list'

list_version = random.randint(0,2000000000)
def invalidate_cache(request=None):
    global list_version
    list_version += 1
    cache.delete(LIST_CACHE_KEY)

def _generate_cache_key(request):
    global list_version
    return '-'.join([generate_cache_key(request), str(list_version)])


#-------------------------------------------------------------------------------
# Community Views
#-------------------------------------------------------------------------------

@view_config(route_name='comunity')
@web
def comunity(request):
    return action_ok()


@view_config(route_name='comunity_login')
@web
def comunity_login(request):
    return action_ok()


@view_config(route_name='comunity_list')
@web
def comunity_list(request):

    def get_all_tracks_dict():
        return [
            track.to_dict('full', exclude_fields=('lyrics','attachments','image')) \
            for track in DBSession.query(Track) \
                .order_by(Track.source_filename) \
                .options( \
                    joinedload(Track.tags), \
                    #joinedload(Track.attachments), \
                    joinedload('tags.parent'), \
                    #joinedload('lyrics'), \
                )
        ]

    tracks = cache.get_or_create(LIST_CACHE_KEY, get_all_tracks_dict)
    
    #path = request.registry.settings['static.media']
    return action_ok(data={
        #'folders': [folder for folder in os.listdir(path) if os.path.isdir(os.path.join(path,folder))],
        'tracks': tracks
    })


@view_config(route_name='comunity_track')
@web
def comunity_track(request):
    return action_ok()
