<%inherit file="_base.mako"/>


## AllanC - ****! I need the slash here because of the broken routing ... rarararar
<a href="/search/tags/"   data-role="button">Browser Tracks</a>
<a href="/queue"          data-role="button">Queue         </a>
<!-- <a href="/fave"           data-role="button">Fave's    </a> -->

% if identity.get('admin', False):
<a href="track_list" data-role="button">List All Tracks</a>
<a href="/admin"     data-role="button">Exit Admin Mode</a>
% endif

