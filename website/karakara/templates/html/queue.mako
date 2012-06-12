<%inherit file="_base.mako"/>

<%def name="title()">Queue</%def>

<%def name="body()">

    <table>
        <tr><th>id</th><th>track_id</th><th>performer_name</th></tr>
        % for queue_item in data.get('list',[]):
        <tr><td>${queue_item['id']}</td><td>${queue_item['track_id']}</td><td>${queue_item['performer_name']}</td></tr>
        % endfor
    </table>

</%def>