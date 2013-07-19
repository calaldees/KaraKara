<%inherit file="_base.mako"/>

## Easter Egg for users who look at the code
<!--
    Welcome iquisitive hax0r!
    Those who look at code deserve a treat.
    
    Navigate to '/settings' to look under the hood at the current settings.
    If you want to look futher then checkout the github repo
        http://github.com/calaldees/karakara/
    Send us a message, get involved, submit a feature request or contribute a new feature yourself.
-->


<% disbaled_message = request.registry.settings.get('karakara.template.menu.disable') %>
% if not identity.get('admin', False) and disbaled_message:
    <p>${disbaled_message}</p>
% else:
    <a href="/search_tags/"   data-role="button">Explore tracks</a>
    <a href="/queue"          data-role="button">Queued tracks </a>
    
    % if identity.get('faves',[]):
    <a href="/fave"           data-role="button">My favorites</a>
    % endif
    
    <a href="/feedback"       data-role="button">Give Feedback</a>    
% endif

% if identity.get('admin', False):
    <a href="/player/player.html" data-role="button" data-theme="e">Player Interface</a>
    <a href="/track_list" data-role="button" data-theme="e">List All Tracks</a>
    <a href="/settings"   data-role="button" data-theme="e">Settings</a>
    <a href="/admin_lock" data-role="button" data-theme="e">Admin Lock</a>
    <a href="/remote"     data-role="button" data-theme="e">Remote Control</a>
    <a href="/admin"      data-role="button" data-theme="e">Exit Admin Mode</a>
% endif
