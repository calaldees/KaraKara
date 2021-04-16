<%inherit file="_base.mako"/>
<%!
import random
import datetime
%>

<%def name="title()">Queue</%def>

<%def name="body()">

    <%
        # Split Queue into 'next' and 'later'(order obscured) lists
        queue = data.get('queue',[])
        split_indexs = data.get('queue_split_indexs')
        if split_indexs and not identity.get('admin'):
            split_index = split_indexs[0]  # TODO: Short term botch until template can be updated to render mutiple split groups
            tracks_next  = queue[:split_index]
            tracks_later = queue[split_index:]
            random.shuffle(tracks_later) # Obscure order of upcomming tracks
        else:
            tracks_next = queue
            tracks_later = []
    %>

    <%def name="btn_remove(queue_item, attrs='')">
        % if identity.get('admin') or identity['id']==queue_item['session_owner']:
        <a href='${paths['context']}?method=delete&format=redirect&queue_item.id=${queue_item['id']}' rel=external ${attrs |n}>remove</a>
        % endif
    </%def>
    <%def name="show_queue_item(queue_item, attrs='')">
        <a href='${paths['track']}/${queue_item['track_id']}' ${attrs |n}>
            <% img_src = h.thumbnail_location_from_track(queue_item['track']) %>
            % if img_src:
            <img src='${img_src}' />
            % endif
            <h3>${queue_item['track']['title']}</h3>
            <p>${queue_item['performer_name'].capitalize()}</p>
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
    <script>
        //$(function() {
        $(document).ready(function() {
            var socket;

            $('.queue-list').sortable().bind('sortupdate', function(e, ui) {
                $('.ui-li-aside').html('');
                var queue_item_id_source      = ui.item.attr('data-queue-item-id');
                var queue_item_id_destination = ui.item.next().attr('data-queue-item-id');
                if (typeof queue_item_id_destination == "undefined") {
                    queue_item_id_destination = 65535;  // should be integer max
                }
                $.ajax({
                    type:'PUT',
                    url:'${paths['context']}.json',
                    dataType:'json',
                    data: 'queue_item.id='+queue_item_id_source+'&queue_item.move.target_id='+queue_item_id_destination,
                    success: function(data, textStatus, jqXHR) {
                        if (!socket) {
                            location.reload();  // only reload if websockets disabled
                        }
                    }//,
                    //error: function(data) {
                    //    console.error(data);
                    //    alert('error moving queue_item')
                    //}
                });
            });

            // Connect to websocket to subscribe to queue events to reload page
            ## No need to authenticate websocket because we are just reading the stream
            ## It may be possible to have this funcationality for all users - just being cautions for now, don't want to overload the websocket server
            ## You get some funky behaviour where the websocket refreshes before the first format=redirect happens, so the success message appears on the queue screen.
            try {
                var currently_dragging = false;

                var clientId = "kk-ctrl-";
                var chars = "0123456789ABCDEF";
                for(var i=0; i<8; i++) {clientId += chars.charAt(Math.floor(Math.random()*chars.length));}
                socket = new Paho.MQTT.Client(${self.js_websocket_url()}, clientId);
                socket.connect({
                    reconnect: true,
                    userName: 'karakara',
                    password: 'aeyGGrYJ',
                })

                socket.onMessageArrived = function(msg) {
                    if (currently_dragging==false && msg.topic=='queue') {
                        console.log('queue updated: reloading page');
                        location.reload();
                    }
                };
                // When dragging ensure update events are disabled - after the drag we will reload anyway
                $('html'       ).bind('mousedown', function() {currently_dragging=true; });
                $('html'       ).bind('mouseup'  , function() {currently_dragging=false;});
                $('.queue-list').bind('drop'     , function() {currently_dragging=false;});
                console.info("websocket queue update listener setup");
            }
            catch(e) {
                console.warn('unable to setup websocket queue update listener');
                socket = null;
            }
        });
    </script>
    % endif

</%def>
