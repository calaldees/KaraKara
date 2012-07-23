<%inherit file="_base.mako"/>


<a href="/track_list"     data-role="button">List Tracks</a>
## AllanC - ****! I need the slash here because of the broken routing ... rarararar
<a href="tags/"           data-role="button">Tag Browser</a>
<a href="/queue"          data-role="button">Queue     </a>
<!-- <a href="/fave"           data-role="button">Fave's    </a> -->

% if identity.get('admin', False):
<a href="/admin"       data-role="button">Disable Admin</a>
<a href="track_list_all" data-role="button">Tracks All</a>
% endif

