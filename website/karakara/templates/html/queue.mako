<%inherit file="_base.mako"/>
<%!
import random
%>

<%def name="title()">Queue</%def>

<%def name="body()">

    <%
        # Break Queue into sections
        #  - the next 15 mins of tracks in order
        #  - tracks after 15 mins randomized
        
        queue_padding = h.get_setting('karakara.queue_padding', request, 'time')
        queue_visible = h.get_setting('karakara.queue_visible', request, 'time')
        total_duration_split = queue_visible.hour*60*60 + queue_visible.minute*60 + queue_visible.second
        
        total_duration = 0
        queue = data.get('queue',[])
        for queue_item in queue:
            queue_item['total_duration'] = total_duration
            total_duration += queue_item['track']['duration']
        
        tracks_next  = [q for q in queue if q['total_duration'] <= total_duration_split]
        tracks_later = [q for q in queue if q['total_duration'] >  total_duration_split]
        random.shuffle(tracks_later)
    %>

    <ul data-role="listview" data-split-icon="minus" data-divider-theme="a">
        ##<li data-role="list-divider">Next Tracks</li>
        % for queue_item in tracks_next:
        <li>
            <a href='${h.track_url(queue_item['track_id'])}'>
                <img src='${h.thumbnail_location_from_track(queue_item['track'])}' />
                <h3>${queue_item['track']['title']}</h3>
                <p>${queue_item['performer_name']}</p>
                <p class="ui-li-aside">${h.duration_str(queue_item['total_duration'])}</p>
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
        % endfor
    </ul>
    
    ##<li data-role="list-divider">Comming soon</li>
    <h2>Comming Soon</h2>
    <% block_lookup = ['a','b','c'] %>
    <div class="ui-grid-${block_lookup[len(block_lookup)-2]} ui-responsive">
        % for queue_item in tracks_later:
        <div class="ui-block-${block_lookup[loop.index%len(block_lookup)]}"><div class="ui-body ui-body-d">${queue_item['track_id']}</div></div>
        % endfor
    </div>

</%def>