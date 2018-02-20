<%inherit file="_base.mako"/>

<%def name="title()">Remote Control</%def>

<script>
    var socket = null;
    $(document).ready(function() {
        try {
            socket = new WebSocket(${self.js_websocket_url()});
            socket.onopen = function(){  //Authenicate client with session key on socket connect
                socket.send(document.cookie.match(/${request.registry.settings['session.cookie_name']}=([^;\s]+)/)[1]);
            };
        }
        catch(err) {
            console.error("Websockets not supported. Using request method", err);
        }
    });

    function send(message) {
        if (socket != null) {
            socket.send(message);
            return false;
        }
        return true;
    }
</script>

<%
    skip_sec = request.queue.settings['karakara.player.video.skip.seconds']
    buttons = (
        ('play'          , _('mobile.remote.play')),
        ('pause'         , _('mobile.remote.pause')),
        ('seek_forwards' , _('mobile.remote.seek +${skip_sec}', mapping={'skip_sec': skip_sec})),
        ('seek_backwards', _('mobile.remote.seek -${skip_sec}', mapping={'skip_sec': skip_sec})),
        ('stop'          , _('mobile.remote.stop')),
        ('skip'          , _('mobile.remote.skip')),
    )
%>
% for cmd, title in buttons:
    <a href='?cmd=${cmd}' data-role="button" onclick='return send("${cmd}");'>${title}</a>
% endfor
