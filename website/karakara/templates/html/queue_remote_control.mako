<%inherit file="_base.mako"/>

<%def name="title()">Remote Control</%def>

<script>
    var socket = null;
    $(document).ready(function() {
        try {
            var clientId = "kk-ctrl-";
            var chars = "0123456789ABCDEF";
            for(var i=0; i<8; i++) {clientId += chars.charAt(Math.floor(Math.random()*chars.length));}
            socket = new Paho.MQTT.Client(${self.js_websocket_url()}, clientId);
            socket.connect({reconnect: true})
        }
        catch(err) {
            console.error("Websockets not supported. Using request method", err);
        }
    });

    function send(message) {
        if (socket != null) {
            console.log('send', message);
            socket.send("karakara/queue/${request.queue.id}", message);
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
