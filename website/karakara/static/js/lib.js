
function timedelta_str(timedelta) {
    var seconds_total = Math.floor(timedelta/1000);
    var seconds       = seconds_total % 60;
    var minutes       = Math.floor(seconds_total/60);
    if (minutes>=1) {
        return minutes+"min";
    }
    if (seconds==0) {
        return "Now";
    }
    return seconds+"sec";
}

function randomize(array) {
    array.sort(function(){return 0.5-Math.random();});
}

function getUrlParameter(sParam) {
    //http://stackoverflow.com/questions/19491336/get-url-parameter-jquery
    // TODO: ES6 this
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
            return decodeURIComponent(sParameterName[1]);
        }
    }
    return '';
}