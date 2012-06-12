<%inherit file="_base.mako"/>

<%def name="title()">Queue</%def>

<%def name="body()">

    <ul data-role="listview" data-split-icon="minus">
        <% total_duration = 0 %>
        % for queue_item in data.get('list',[]):
        <li>
            <a href='${h.track_url(queue_item['track_id'])}'>
                % if queue_item['image']:
                <img src='${h.media_url(queue_item['image'])}' />
                % endif
                <h3>${queue_item['track']['title']}</h3>
                <p>${queue_item['performer_name']}</p>
                <p class="ui-li-aside">${h.duration_str(total_duration)}</p>
            </a>
            % if identity['admin'] or identity['id']==queue_item['session_owner']:
            <a href='/queue?method=delete&format=redirect&queue_item.id=${queue_item['id']}' rel=external>remove</a>
            <%doc>
            <form action="/queue" method="POST">
                <input type="hidden" name="method"        value="DELETE" />
                <input type="hidden" name="format"        value="redirect" />
                <input type="hidden" name="queue_item.id" value="${queue_item['id']}" />
                <input type="submit" name="submit_remove" value="delete" />
            </form>
            </%doc>
            % endif
        </li>
        <% total_duration += queue_item['track']['duration'] %>
        % endfor
    </ul>

</%def>