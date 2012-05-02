<%inherit file="_base.mako"/>

<h2>Track List</h2>

<ul data-role="listview" data-inset="true">
    % for track_id in data['list']:
    <li><a href="/track/${track_id}">${track_id}</a></li>
    % endfor
</ul>