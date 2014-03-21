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
def invalidate_list_cache(request=None):
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
        # Get tracks from db
        tracks = [
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
        
        # Get track folders from media source
        media_path = request.registry.settings['static.media']
        media_folders = set((folder for folder in os.listdir(media_path) if os.path.isdir(os.path.join(media_path, folder))))
        
        # Compare folder sets to identify unimported/renamed files
        track_folders = set((track['source_filename'] for track in tracks))
        not_imported = media_folders.difference(track_folders)
        missing_source = track_folders.difference(media_folders)
        
        return {
            'tracks': tracks,
            'not_imported': sorted(not_imported),
            'missing_source': sorted(missing_source),
        }

    data_tracks = cache.get_or_create(LIST_CACHE_KEY, get_all_tracks_dict)
    return action_ok(data=data_tracks)


@view_config(route_name='comunity_track')
@web
def comunity_track(request):
    return action_ok()
