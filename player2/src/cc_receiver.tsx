function _castReceiver(dispatch, props) {
    let crm = cast.receiver.CastReceiverManager.getInstance();
    crm.onReady = function (event) {
        crm.setApplicationState("Application ready");
    };
    let bus = crm.getCastMessageBus('urn:x-cast:uk.karakara');
    bus.onMessage = function (event) {
        var msg = JSON.parse(event.data);
        console.groupCollapsed("cast_onmessage(", event.target ,")")
        console.log(msg);
        console.groupEnd();
        dispatch(function (state) {
            return {
                ...state,
                room_name: msg.room_name,
                room_password: msg.room_password
            };
        });
        //bus.send(event.senderId, event.data);
    }
    crm.start({ statusText: "Application starting" });

    return function () {
        crm.stop();
    }
}

export function CastReceiver(): Subscription {
    return [_castReceiver, {}];
}