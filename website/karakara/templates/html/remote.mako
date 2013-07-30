<%inherit file="_base.mako"/>

<%def name="title()">Remote Control</%def>

<script>
    var socket = null;
    $(document).ready(function() {
        var host = location.hostname;
        var port = ${request.registry.settings['karakara.websocket.port']};
        try {
            socket = new WebSocket("ws://" + host + ":" + port + "/");
            socket.onopen = function(){  //Authenicate client with session key on socket connect
                socket.send(document.cookie.match(/${request.registry.settings['session.key']}=(.+?)(\;|\b)/)[1]);
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

<a href='?cmd=play' data-role="button" onclick='return send("play");'>Play Fullscreen</a>
<a href='?cmd=pause' data-role="button" onclick='return send("pause");'>Pause (Toggle)</a>
<a href='?cmd=seek' data-role="button" onclick='return send("seek");'>Seek (30sec)</a>
<a href='?cmd=stop' data-role="button" onclick='return send("stop");'>Stop</a>
<a href='?cmd=skip' data-role="button" onclick='return send("skip");'>Skip Track</a>