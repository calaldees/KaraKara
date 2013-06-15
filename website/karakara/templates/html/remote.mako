<%inherit file="_base.mako"/>

<%def name="title()">Remote Control</%def>
<script>
    var socket = null;
    $(document).ready(function() {
        var host = location.hostname;
        var port = ${request.registry.settings['karakara.websocket.port']};
        try {
            socket = new WebSocket("ws://" + host + ":" + port + "/");
        }
        catch(err) {
            //alert("Websockets not supported. using request method");
        }
    });
    
    function send(message) {
        if (socket != null) {
            socket.send(message);
            alert("websocket sent");
            return false;
        }
        return true;
        
        
    }
</script>

Big Screen Remote Control

<a href='?cmd=play' data-role="button" onclick='return send("play");'>Play</a>
<a href='?cmd=pause' data-role="button" onclick='return send("pause");'>Pause</a>
<a href='?cmd=skip' data-role="button" onclick='return send("skip");'>Skip</a>