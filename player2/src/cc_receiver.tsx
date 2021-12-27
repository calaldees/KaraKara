/*
Usage: add something like this to your hyperapp `subscriptions` list,
to have the chromecast app set `video_url` in response to the mobile
phone's request.

ChromecastReceiver({
    onMessageLoad: function (state, data) {
        return {...state, video_url: data.media.contentId };
    },
}),
*/

function _chromecastReceiverSub(dispatch, props) {
    // Subscribe: set message interceptor callback and start
    const context = cast.framework.CastReceiverContext.getInstance();
    const playerManager = context.getPlayerManager();

    if (props.onMessageLoad) {
        playerManager.setMessageInterceptor(
            cast.framework.messages.MessageType.LOAD,
            function (data) {
                dispatch(props.onMessageLoad, data);
                return null;
            },
        );
    }

    // TODO: options from props
    const options = new cast.framework.CastReceiverOptions();
    options.disableIdleTimeout = true;

    context.start(options);

    // Unsubscribe: remove interceptor callback and stop
    return function () {
        if (props.onMessageLoad) {
            playerManager.setMessageInterceptor(
                cast.framework.messages.MessageType.LOAD,
                null,
            );
        }
        context.stop();
    };
}

export function ChromecastReceiver(props) {
    return [_chromecastReceiverSub, props];
}
