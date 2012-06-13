$(document).bind("mobileinit", function(){
    // Sets defaults for jquery mobile
    /*
    $.mobile.page.prototype.options.degradeInputs.date = 'text';
    $.mobile.defaultDialogTransition    = 'fade';
    $.mobile.ajaxEnabled = false;
    $.mobile.selectmenu.prototype.options.nativeMenu = false;
    $.mobile.fixedToolbars.setTouchToggleEnabled(false);
    */
});

//$(document).bind("pagecreate", function() {
//    $('form').attr('data-ajax', 'false'); // Little hacky, tell any forms created not to ajax submit
//});

function isiPhone() {
    return (
        (navigator.platform.indexOf("iPhone") != -1) ||
        (navigator.platform.indexOf("iPod"  ) != -1)
    );
}
function isWebOS() {
    return (
        (navigator.userAgent.indexOf("webOS") != -1) ||
        (navigator.userAgent.indexOf("hpwOS") != -1)
    );
}

// AllanC: Horrible fix for jQueryMobile background problems on WebOS devices
$(document).bind('pageinit', function() {
    if (isWebOS()) {
        $('.ui-content, .ui-page').attr('style','background: #EEEEEE; !important;');
    }
});

