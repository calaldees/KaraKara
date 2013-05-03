<%inherit file="_base.mako"/>
<%!
import random
import datetime
%>

<%def name="title()">Queue</%def>

<%def name="body()">

    <%
        # Break Queue into sections
        #  - the next 15 mins of tracks in order
        #  - tracks after 15 mins randomized
        
        time_padding = request.registry.settings.get('karakara.queue.template.padding')
        time_visible = request.registry.settings.get('karakara.queue.template.visible')
        
        # Overlay 'total_duration' on all tracks
        # It takes time for performers to change, so each track add a padding time
        total_duration = datetime.timedelta(seconds=0)
        queue = data.get('queue',[])
        for queue_item in queue:
            queue_item['total_duration'] = total_duration + time_padding
            total_duration += datetime.timedelta(seconds=queue_item['track']['duration'])
        
        # Setup the separate 'next' and 'later' lists
        # 'next' tracks are shown in order
        # 'later' tracks order is obscured
        # admin users always see the complete ordered queue
        if time_visible and not identity.get('admin'):
            tracks_next  = [q for q in queue if q['total_duration'] <= time_visible]
            tracks_later = [q for q in queue if q['total_duration'] >  time_visible]
            random.shuffle(tracks_later) # Obscure order of upcomming tracks
        else:
            tracks_next = queue
            tracks_later = []
    %>

    <%def name="btn_remove(queue_item, attrs='')">
        % if identity.get('admin') or identity['id']==queue_item['session_owner']:
        <a href='/queue?method=delete&format=redirect&queue_item.id=${queue_item['id']}' rel=external ${attrs |n}>remove</a>
        % endif
    </%def>
    <%def name="show_queue_item(queue_item, attrs='')">
        <a href='${h.track_url(queue_item['track_id'])}' ${attrs |n}>
            <% img_src = h.thumbnail_location_from_track(queue_item['track']) %>
            % if img_src:
            <img src='${img_src}' />
            % endif
            <h3>${queue_item['track']['title']}</h3>
            <p>${queue_item['performer_name']}</p>
            <p class="ui-li-aside">${h.duration_str(queue_item['total_duration'])}</p>
        </a>

    </%def>

    <%doc>
        Queued Tracks - (within the next karakara.queue_visible time)
        The tracks are shown in a list with image previews
        we will always have tracks_next (even if it is empty)
    </%doc>
    <ul data-role="listview" data-split-icon="minus" data-divider-theme="a" class="queue-list">
        ##<li data-role="list-divider">Next Tracks</li>
        % for queue_item in tracks_next:
        <li data-queue-item-id="${queue_item['id']}">
            ${show_queue_item(queue_item)}
            ${btn_remove(queue_item)}
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
    ##<h2>Coming up ...</h2>
    ##<% block_lookup = ['a','b','c'] %>
    <ul class="queue-grid">
    ##<div class="ui-grid-${block_lookup[len(block_lookup)-2]} ui-responsive">
        % for queue_item in tracks_later:
        <li>
        ##<div class="ui-block-${block_lookup[loop.index%len(block_lookup)]}">
            ##<div class="ui-body ui-body-d">
            ${show_queue_item(queue_item, 'data-role="button" data-theme="c" data-mini="true" data-shadow="false" data-corners="false"')}
            ${btn_remove(queue_item, 'data-role="button" data-icon="minus" data-iconpos="notext" data-inline="true" data-theme="b"')}
            ##</div>
        </li>
        % endfor
    </ul>
    % endif

    % if identity.get('admin'):
    <script src="${h.static_url('jquery/jquery.sortable.js')}"></script>
    <script>
        $(function() {
            $('.queue-list').sortable().bind('sortupdate', function(e, ui) {
                $('.ui-li-aside').html('');
                var queue_item_id_source      = ui.item.attr('data-queue-item-id');
                var queue_item_id_destination = ui.item.next().attr('data-queue-item-id');
                $.ajax({
                    type:'PUT',
                    url:'/queue.json',
                    dataType:'json',
                    data: 'queue_item.id='+queue_item_id_source+'&queue_item.move.target_id='+queue_item_id_destination,
                    success: function(data) {
                        //console.log(queue_item_id_source, queue_item_id_destination);
                    },
                    error: function(data) {
                        alert('error moving queue_item')
                    }
                });
            });
        });
    </script>
    % endif

</%def>