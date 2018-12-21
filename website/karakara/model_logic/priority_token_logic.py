import logging
import json

from sqlalchemy.orm.exc import NoResultFound

from calaldees.date_tools import now
from calaldees.json import json_object_handler

from karakara.model import DBSession
from karakara.model.model_priority_token import PriorityToken

from . import TOKEN_ISSUE_ERROR


log = logging.getLogger(__name__)


class PriorityTokenManager():
    def __init__(self, request):
        self.request = request

    @property
    def settings(self):
        return self.request.queue.settings

    @property
    def user_id(self):
        return self.request.session_identity['id']

    def issue(self):
        priority_window = self.settings.get('karakara.queue.add.limit.priority_window')
        # TODO: Depreciate this priority_window settings
        #  This can be auto-calculated from the current average track length in the queue

        # Aquire most recent priority token - if most recent token in past, set recent token to now
        try:
            latest_token = DBSession.query(PriorityToken).filter(PriorityToken.used==False).order_by(PriorityToken.valid_end.desc()).limit(1).one()
            latest_token_end = latest_token.valid_end
        except NoResultFound:
            latest_token_end = None
        if not latest_token_end or latest_token_end < now():
            # When issueing the first priority token
            latest_token_end = now() + priority_window  # get_queue_duration(request) # Adding entire queue here was unnessisary.

        # Do not issue tokens past the end of the event
        event_end = self.settings.get('karakara.event.end')
        if event_end and latest_token_end > event_end:
            # Unable to issue token as event end
            log.debug('priority_token rejected - event end')
            return TOKEN_ISSUE_ERROR.EVENT_END

        # TODO: possibly depricate this - we can just keep staking tokens until the end of the event
        priority_token_limit = self.settings.get('karakara.queue.add.limit.priority_token')
        if priority_token_limit and latest_token_end > now()+priority_token_limit:
            # Unable to issue token as priority tokens are time limited
            log.debug('priority_token rejected - token limit')
            return TOKEN_ISSUE_ERROR.TOKEN_LIMIT

        # TODO: Look at the last priority tokens created and raise a warning if the token is likely to pass beyond the end of the event.

        # Do not issue another priority_token if current user already has a priority_token
        try:
            priority_token = DBSession.query(PriorityToken) \
                                .filter(PriorityToken.used==False) \
                                .filter(PriorityToken.session_owner==self.user_id) \
                                .filter(PriorityToken.valid_end>now()) \
                                .one()
            if priority_token:
                log.debug('priority_token rejected - existing token')
                return TOKEN_ISSUE_ERROR.TOKEN_ISSUED
        except NoResultFound:
            pass

        # Issue the new token
        priority_token = PriorityToken()
        priority_token.session_owner = self.user_id
        priority_token.valid_start = latest_token_end
        priority_token.valid_end = latest_token_end + priority_window
        DBSession.add(priority_token)

        # TODO: replace with new one in lib
        #request.response.set_cookie('priority_token', json_cookie);  # WebOb.set_cookie mangles the cookie with m.serialize() - so I rolled my own set_cookie
        priority_token_dict = priority_token.to_dict()
        priority_token_dict.update({
            'server_datetime': now(),  # The client datetime and server datetime may be out. we need to return the server time so the client can calculate the difference
        })
        json_cookie = json.dumps(priority_token_dict, default=json_object_handler)
        self.request.response.headerlist.append(('Set-Cookie', 'priority_token={0}; Path=/'.format(json_cookie)))
        #self.request.response.set_cookie(name='priority_token', value=json_cookie, path='/', overwrite=True)  # This method butchers the json and cannot be used

        log.debug('priority_token issued')
        return priority_token

    def consume(self):
        try:
            token = DBSession.query(PriorityToken) \
                .filter(PriorityToken.used == False) \
                .filter(PriorityToken.session_owner == self.user_id) \
                .filter(PriorityToken.valid_start <= now(), PriorityToken.valid_end > now()) \
                .one()
            token.used = True
            self.request.response.delete_cookie('priority_token')
            log.debug('priority_token consumed')
            return True
        except NoResultFound:
            return False
