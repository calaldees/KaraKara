<%inherit file="_base.mako"/>

<%def name="title()">Queue</%def>

<%def name="body()">

    <ul data-role="listview" data-split-icon="minus">
        % for queue_item in data.get('list',[]):
        <li>
            <a href='${h.track_url(queue_item['track_id'])}'>
                % if queue_item['image']:
                <img src='${h.media_url(queue_item['image'])}' />
                % endif
                <h3>${queue_item['track']['title']}</h3>
                <p>${queue_item['performer_name']}</p>
            </a>
            % if identity['admin'] or identity['id']==queue_item['session_owner']:
            <a href='#'>remove</a>
            % endif
        </li>
        % endfor
    </ul>

</%def>