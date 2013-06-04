
function timedelta_str(timedelta) {
    var seconds_total = Math.floor(timedelta/1000);
    var seconds       = seconds_total % 60;
    var minutes       = Math.floor(seconds_total/60);
    if (minutes>=1) {
        return minutes+"min";
    }
    return seconds+"sec";
}

function randomize(array) {
    array.sort(function(){return 0.5-Math.random();});
}
