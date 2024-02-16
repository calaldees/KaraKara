function _castSender(dispatch, props) {
    var applicationID = '05C10F57';
    var session = null;

    function bail(e) {
        console.log("cast error", e);
        dispatch((state) => ({...state, casting: false}));
    }

    var apiConfig = new chrome.cast.ApiConfig(
        new chrome.cast.SessionRequest(applicationID),
        function (s) { console.log("session", s); },  // session listener
        function (r) { console.log("receiver", r); }, // receiver listener
    );
    chrome.cast.initialize(
        apiConfig,
        function () { },  // ok
        function (e) { bail(e); },  // err
    );
    chrome.cast.requestSession(
        function (s) {
            session = s;
            session.setReceiverMuted(false);
            session.setReceiverVolumeLevel(1.00);
            session.sendMessage('urn:x-cast:uk.karakara', {
                "command": "join",
                "room_name": props.room_name,
                "room_password": props.room_password,
            });
        },
        function (e) {bail(e);}
    );

    return function () {
        if (session) {
            session.stop(
                function () { session = null; },
                function (e) { console.log("session stop err", e); },
            );
        }
    }
}

export function CastSender(name, pass): Subscription {
    return [_castSender, { room_name: name, room_password: pass }];
}
