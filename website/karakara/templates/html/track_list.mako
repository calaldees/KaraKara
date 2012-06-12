<%inherit file="_base.mako"/>

<%def name="title()">All Tracks</%def>

<ul data-role="listview" data-filter="true">
    % for track_id in data['list']:
    <li><a href="${h.track_url(track_id)}">${track_id}</a></li>
    % endfor
</ul>