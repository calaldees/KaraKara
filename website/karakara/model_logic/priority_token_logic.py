

def issue_priority_token(request, DBSession):
    priority_window = request.registry.settings.get('karakara.queue.add.limit.priority_window')

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
    event_end = request.registry.settings.get('karakara.event.end')
    if event_end and latest_token_end > event_end:
        # Unable to issue token as event end
        log.debug('priority_token rejected - event end')
        return TOKEN_ISSUE_ERROR.EVENT_END

    priority_token_limit = request.registry.settings.get('karakara.queue.add.limit.priority_token')
    if priority_token_limit and latest_token_end > now()+priority_token_limit:
        # Unable to issue token as priority tokens are time limited
        log.debug('priority_token rejected - token limit')
        return TOKEN_ISSUE_ERROR.TOKEN_LIMIT

    # Do not issue another priority_token if current user alrady has a priority_token
    try:
        priority_token = DBSession.query(PriorityToken) \
                            .filter(PriorityToken.used==False) \
                            .filter(PriorityToken.session_owner==request.session['id']) \
                            .filter(PriorityToken.valid_end>now()) \
                            .one()
        if priority_token:
            log.debug('priority_token rejected - existing token')
            return TOKEN_ISSUE_ERROR.TOKEN_ISSUED
    except NoResultFound:
        pass

    # Issue the new token
    priority_token = PriorityToken()
    priority_token.session_owner = request.session['id']
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
    request.response.headerlist.append(('Set-Cookie', 'priority_token={0}; Path=/'.format(json_cookie)))

    log.debug('priority_token issued')
    return priority_token


def consume_priority_token(request, DBSession):
    try:
        token = DBSession.query(PriorityToken) \
            .filter(PriorityToken.used == False) \
            .filter(PriorityToken.session_owner == request.session['id']) \
            .filter(PriorityToken.valid_start <= now(), PriorityToken.valid_end > now()) \
            .one()
        token.used = True
        request.response.delete_cookie('priority_token')
        log.debug('priority_token consumed')
        return True
    except NoResultFound:
        return False
