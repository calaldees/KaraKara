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
        def totalseconds(time):
            if time:
                return time.hour*60*60 + time.minute*60 + time.second
            return 0
        
        time_padding = totalseconds(h.get_setting('karakara.queue_padding', request, 'time') or 0)
        time_visible = totalseconds(h.get_setting('karakara.queue_visible', request, 'time') or 0)
        
        # Overlay 'total_duration' on all tracks
        total_duration = 0
        queue = data.get('queue',[])
        for queue_item in queue:
            queue_item['total_duration'] = total_duration + time_padding
            total_duration += queue_item['track']['duration']
        
        if time_visible:
            tracks_next  = [q for q in queue if q['total_duration'] <= time_visible]
            tracks_later = [q for q in queue if q['total_duration'] >  time_visible]
            random.shuffle(tracks_later) # Obscure order of upcomming tracks
        else:
            tracks_next = queue
            tracks_later = []
    %>

    <%def name="show_queue_item(queue_item, show_estimated_time=True)">
        <a href='${h.track_url(queue_item['track_id'])}'>
            <% img_src = h.thumbnail_location_from_track(queue_item['track']) %>
            % if img_src:
            <img src='${img_src}' />
            % endif
            <h3>${queue_item['track']['title']}</h3>
            <p>${queue_item['performer_name']}</p>
            % if show_estimated_time:
            <p class="ui-li-aside">${h.duration_str(queue_item['total_duration'])}</p>
            % endif
        </a>
        % if identity['admin'] or identity['id']==queue_item['session_owner']:
        <a href='/queue?method=delete&format=redirect&queue_item.id=${queue_item['id']}' rel=external>remove</a>
        % endif
    </%def>

    <%doc>
        Queued Tracks - (within the next karakara.queue_visible time)
        The tracks are shown in a list with image previews
        we will always have tracks_next (even if it is empty)
    </%doc>
    <ul data-role="listview" data-split-icon="minus" data-divider-theme="a">
        ##<li data-role="list-divider">Next Tracks</li>
        % for queue_item in tracks_next:
        <li>
            ${show_queue_item(queue_item)}
        </li>
        % endfor
    </ul>

    <%doc>
        Queued Tracks after - karakara.queue_visible time
        These tracks are not shown in order as admins may want to shuffle the order of play
        without causing a huge uproar of favoratisum.
        The feature exisits because 3 big long tracks in a row can kill a Karaokoe
    </%doc>
    % if tracks_later:
    <h2>Coming up ...</h2>
    <% block_lookup = ['a','b','c'] %>
    <div class="ui-grid-${block_lookup[len(block_lookup)-2]} ui-responsive">
        % for queue_item in tracks_later:
        <div class="ui-block-${block_lookup[loop.index%len(block_lookup)]}">
            ##<div class="ui-body ui-body-d">
            ${show_queue_item(queue_item, show_estimated_time=False)}
            ##</div>
        </div>
        % endfor
    </div>
    % endif

</%def>