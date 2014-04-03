from pyramid.view import view_config

import os
import random
import hashlib
import time
import re
import json
from collections import namedtuple

from sqlalchemy.orm import joinedload
from sqlalchemy.orm.exc import NoResultFound

from externals.lib.misc import backup
from externals.lib.social import facebook

from ..model              import DBSession, commit
from ..model.model_tracks import Track
from ..model.model_comunity import ComunityUser, SocialToken

from . import web, action_ok, action_error, cache, generate_cache_key, comunity_only

from ..templates import helpers as h

import logging
log = logging.getLogger(__name__)


ProviderToken = namedtuple('ProviderToken', ['provider', 'token'])

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
# Community Utils
#-------------------------------------------------------------------------------

class ComunityTrack():
    def __init__(self, request, track_id):
        self.media_path = request.registry.settings['static.media']
        self.track_id = track_id
        self._track_dict = None
    
    @property
    def track(self):
        if not self._track_dict:
            self._track_dict = DBSession.query(Track) \
                .options( \
                    joinedload(Track.tags), \
                    joinedload(Track.attachments), \
                    joinedload('tags.parent'), \
                    joinedload('lyrics'), \
                ) \
                .get(self.track_id).to_dict('full')
        return self._track_dict
    
    @property
    def path(self):
        return os.path.join(self.media_path, self.track['source_filename'])
    @property
    def path_backup(self):
        return os.path.join(self.path, '_old_versions')
    @property
    def tag_data_filename(self):
        return os.path.join(self.path, 'tags.txt')
    @property
    def tag_data_raw(self):
        with open(self.tag_data_filename ,'r') as tag_data_filehandle:
            return tag_data_filehandle.read()
    @tag_data_raw.setter
    def tag_data_raw(self, tag_data):
        backup(self.tag_data_filename, self.path_backup)
        with open(self.tag_data_filename ,'w') as tag_data_filehandle:
            tag_data_filehandle.write(tag_data)
    @property
    def tag_data(self):
        return {tuple(line.split(':')) for line in self.tag_data_raw.split('\n')}
    @property
    def source_data_filename(self):
        return os.path.join(self.path, 'sources.json')
    @property
    def source_data(self):
        with open(self.source_data_filename ,'r') as source_data_filehandle:
            return json.load(source_data_filehandle)
    @property
    def subtitle_filenames(self):
        return [k for k in self.source_data.keys() if re.match(r'^.*\.(ssa|srt)$', k)]
    @property
    def subtitle_data(self):
        def subtitles_read(subtitle_filename):
            with open(os.path.join(self.path, 'source', subtitle_filename) ,'r') as subtitle_filehandle:
                return subtitle_filehandle.read()
        return dict(((subtitle_filename, subtitles_read(subtitle_filename)) for subtitle_filename in self.subtitle_filenames))



#-------------------------------------------------------------------------------
# Community Views
#-------------------------------------------------------------------------------

@view_config(route_name='comunity')
@web
def comunity(request):
    return action_ok()

@view_config(route_name='comunity_logout')
@web
def comunity_logout(request):
    request.session['comunity'] = {}
    return action_ok()

@view_config(route_name='comunity_login')
@web
def comunity_login(request):
    user = None
    provider_token = None
    
    # Auto login if no service keys are provided
    if request.registry.settings.get('karakara.server.mode') == 'development' and not request.registry.settings.get('facebook.secret'):
        request.session['comunity'] = {
            'username': 'developer',
            'avatar'  : h.static_url('dev_avatar.png'),
            'approved': True,
        }
        return action_ok()

    # Step 1 - Direct user to 3rd party login dialog ---------------------------
    if not request.session.get('comunity') and not request.params.get('code'):
        if 'csrf_token' not in request.session:
            sha1_hash = hashlib.sha1()
            sha1_hash.update(str(time.time()).encode('utf-8'))
            request.session['csrf_token'] = sha1_hash.hexdigest()
        facebook_dialog_url = facebook.login_dialog_url(
            appid=request.registry.settings.get('facebook.appid'),
            csrf_token=request.session['csrf_token'],
            permissions=request.registry.settings.get('facebook.permissions'),
            redirect_uri=request.path_url,
        )
        return action_ok(data=dict(facebook_dialog_url=facebook_dialog_url))
    
    # Step 2 - Lookup full 3rd party access_token with token from dialog -------
    
    # Facebook
    if request.params.get('code') and request.params.get('state'):
        if request.params.get('state') != request.session.get('csrf_token'):
            raise action_error(message='csrf mismatch', code=400)
        # Check submited code with facebook
        response = facebook.call_api(
            'oauth/access_token',
            client_id     = request.registry.settings.get('facebook.appid'),
            client_secret = request.registry.settings.get('facebook.secret'),
            redirect_uri  = request.path_url,
            code          = request.params.get('code'),
        )
        provider_token = ProviderToken('facebook', response.get('access_token'))
        if not provider_token.token:
            raise action_error(message=response.get('error') or 'error with facebook')
    
    # Safty check - we have provider token
    if not provider_token:
        error_message = 'no token provided by any service'
        log.error(error_message)
        raise action_error(message=error_message)
    
    # Step 3 - Lookup local user_id OR create local user with details from 3rd party service
    try:
        user = DBSession.query(ComunityUser).join(SocialToken).filter(SocialToken.token==provider_token.token).one()
    except NoResultFound:
        user = ComunityUser()
        
        if provider_token.provider == 'facebook':
            fb = facebook.facebook(access_token=provider_token.token)
            user_data = fb.api('me')
            user.tokens.append(SocialToken(token=provider_token.token, provider=provider_token.provider, data=user_data))
            user.name = '{first_name} {last_name}'.format(**user_data)
        
        DBSession.add(user)
        commit()
        DBSession.add(user)
        request.session['comunity'] = {'id': user.id}
    
    # Step 4 - lookup local user and set session details
    user_id = request.session.get('comunity',{}).get('id')
    try:
        user = user or DBSession.query(ComunityUser).filter(ComunityUser.id==user_id).one()  # lookup new user or use user aquired in previous step
        request.session['comunity'] = {
            'username': user.name,
            'provider': 'facebook',  # couple of hard coded facebook params here, if we support more providers this can be tidyed
            'avatar'  : facebook.endpoints['avatar'].format(user.user_data.get('id')),
            'approved': user.approved,
        }
    except NoResultFound:
        error_message  = 'no user {0}'.format(user_id)
        request.session['comunity'] = {}
        log.error(error_message)
        raise action_error(message=error_message)
    
    return action_ok()


@view_config(route_name='comunity_list')
@web
@comunity_only
def comunity_list(request):

    def _comnunity_list():
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

    data_tracks = cache.get_or_create(LIST_CACHE_KEY, _comnunity_list)
    return action_ok(data=data_tracks)


@view_config(route_name='comunity_track', request_method='GET')
@web
@comunity_only
def comunity_track(request):
    ctrack = ComunityTrack(request, request.matchdict['id'])
    return action_ok(data={
        'track': ctrack.track,
        'tag_matrix': {},
        'tag_data': ctrack.tag_data_raw,
        'subtitles': ctrack.subtitle_data,
    })

@view_config(route_name='comunity_track', request_method='POST')
@web
@comunity_only
def comunity_track_update(request):
    ctrack = ComunityTrack(request, request.matchdict['id'])
    # Save tag data
    if 'tag_data' in request.params:
        ctrack.tag_data_raw = request.params['tag_data']
    # backup existing file
    #import pdb ; pdb.set_trace()
    return action_ok()
