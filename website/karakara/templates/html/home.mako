<%inherit file="_base.mako"/>


## AllanC - ****! I need the slash here because of the broken routing ... rarararar
<a href="/search_tags/"   data-role="button">Browser Tracks</a>
<a href="/queue"          data-role="button">Queue         </a>
<!-- <a href="/fave"           data-role="button">Fave's    </a> -->

% if identity.get('admin', False):
<a href="track_list" data-role="button" data-theme="e">List All Tracks</a>
<a href="/admin"     data-role="button" data-theme="e">Exit Admin Mode</a>
% endif

