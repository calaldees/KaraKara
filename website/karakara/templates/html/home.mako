<%inherit file="_base.mako"/>

<a href="/search_tags/"   data-role="button">Explore tracks</a>
<a href="/queue"          data-role="button">Queued tracks </a>
% if identity.get('faves',[]):
<a href="/fave"           data-role="button">My favorites</a>
% endif

<a href="/feedback"       data-role="button">Give Feedback</a>

% if identity.get('admin', False):
<a href="/player/player.html" data-role="button" data-theme="e">Player Interface</a>
<a href="track_list" data-role="button" data-theme="e">List All Tracks</a>
<a href="/settings"  data-role="button" data-theme="e">Settings</a>
<a href="/admin_lock" data-role="button" data-theme="e">Admin Lock</a>
<a href="/admin"     data-role="button" data-theme="e">Exit Admin Mode</a>
% endif
