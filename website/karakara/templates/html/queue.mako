<%inherit file="_base.mako"/>

<%def name="title()">Queue</%def>

<%def name="body()">

## data-role="listview"

    <ul data-role="listview" data-split-icon="minus">
        % for queue_item in data.get('list',[]):
        <li>
            <a href='#'>
                % if queue_item['image']:
                <img src='${queue_item['image']}' />
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