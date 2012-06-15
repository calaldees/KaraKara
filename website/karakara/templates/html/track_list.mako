<%inherit file="_base.mako"/>

<%def name="title()">All Tracks</%def>

<ul data-role="listview" data-filter="true">
    % for track in data['list']:
    <li><a href="${h.track_url(track['id'])}">${track['title']}</a></li>
    % endfor
</ul>