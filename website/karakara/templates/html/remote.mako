<%inherit file="_base.mako"/>

<%def name="title()">Remote Control</%def>

<script>
    var socket = null;
    $(document).ready(function() {
        try {
            socket = new WebSocket("ws://" + location.hostname + ":" + ${request.registry.settings['karakara.websocket.port']} + "/");
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

<%
    skip_sec = request.registry.settings['karakara.player.video.skip.seconds']
    buttons = (
        ('play'          , 'Play Fullscreen'                ),
        ('pause'         , 'Pause (toggle)'                 ),
        ('seek_forwards' , 'Seek (+{0}sec)'.format(skip_sec)),
        ('seek_backwards', 'Seek (-{0}sec)'.format(skip_sec)),
        ('stop'          , 'Stop'                           ),
        ('skip'          , 'Skip Track'                     ),
    )
%>
% for cmd, title in buttons:
    <a href='?cmd=${cmd}' data-role="button" onclick='return send("${cmd}");'>${title}</a>
% endfor
