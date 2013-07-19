<%inherit file="_base.mako"/>

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
    <a href="track_list"  data-role="button" data-theme="e">List All Tracks</a>
    <a href="/settings"   data-role="button" data-theme="e">Settings</a>
    <a href="/admin_lock" data-role="button" data-theme="e">Admin Lock</a>
    <a href="/remote"     data-role="button" data-theme="e">Remote Control</a>
    <a href="/admin"      data-role="button" data-theme="e">Exit Admin Mode</a>
% endif
