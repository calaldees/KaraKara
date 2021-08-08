/**
 * Check if the browser can send casts - only include ChromecastSender
 * in the list of subscribers if this is True
 */
export function isCastAvailable() {
    return gCastAvailable;
}
let gCastAvailable = false;
window["__onGCastApiAvailable"] = function (isAvailable) {
    console.log("Casting available?", isAvailable);
    gCastAvailable = isAvailable;
};

/**
 *
 * @param props
 *   receiverApplicationId - string
 *   onCastStateChanged - function(event)
 *   onSessionStateChanged - function(event)
 * @returns
 */
export function ChromecastSender(props) {
    return [_chromecastSenderSub, props];
}
function _chromecastSenderSub(dispatch, props) {
    let context = cast.framework.CastContext.getInstance();
    context.setOptions({
        receiverApplicationId: props.receiverApplicationId,
        autoJoinPolicy: chrome.cast.AutoJoinPolicy.ORIGIN_SCOPED,
    });

    function onCastStateChanged(event) {
        dispatch(props.onCastStateChanged, event);
    }
    if (props.onCastStateChanged) {
        context.addEventListener(
            cast.framework.CastContextEventType.CAST_STATE_CHANGED,
            onCastStateChanged,
        );
    }

    function onSessionStateChanged(event) {
        dispatch(props.onSessionStateChanged, event);
    }
    if (props.onSessionStateChanged) {
        context.addEventListener(
            cast.framework.CastContextEventType.SESSION_STATE_CHANGED,
            onSessionStateChanged,
        );
    }

    return function () {
        if (props.onCastStateChanged) {
            context.removeEventListener(
                cast.framework.CastContextEventType.CAST_STATE_CHANGED,
                onCastStateChanged,
            );
        }
        if (props.onSessionStateChanged) {
            context.removeEventListener(
                cast.framework.CastContextEventType.SESSION_STATE_CHANGED,
                onSessionStateChanged,
            );
        }
        context.endCurrentSession(true); // stop casting
    };
}

/**
 *
 * @param props
 *   contentId - string
 *   contentType - string
 *   credentials - string
 *   onSuccess - function()
 *   onFailure - function(errorCode)
 * @returns
 */
export function LoadMedia(props): Effect {
    return [
        function (dispatch, props) {
            let context = cast.framework.CastContext.getInstance();
            let castSession = context.getCurrentSession();
            var mediaInfo = new chrome.cast.media.MediaInfo(
                props.contentId,
                props.contentType,
            );
            var request = new chrome.cast.media.LoadRequest(mediaInfo);
            request.credentials = props.credentials;
            castSession.loadMedia(request).then(
                function () {
                    if (props.onSuccess) dispatch(props.onSuccess);
                },
                function (errorCode) {
                    if (props.onFailure) dispatch(props.onFailure, errorCode);
                },
            );
        },
        props,
    ];
}
