<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Queue Items</h1>

    <table class="table table-condensed table-hover">
        <tr>
            <th>track_id</th>
            <th>image</th>
            <th>status</th>
            <th>track_title</th>
            <th>performer_name</th>
            <th>time_added</th>
            <th>time_touched</th>
        </tr>
    % for queue_item in data.get('queue', []):
        <tr>
            <td>${queue_item['track_id'][0:5]}</td>
            <% img_src = h.thumbnail_location_from_track(queue_item['track']) %>
            <td><img src="${img_src}" style="width: 64px;"></td>
            <td>${queue_item['status']}</td>
            <td>${queue_item['track'].get('title')}</td>
            <td>${queue_item['performer_name']}</td>
            <td>${queue_item['time_added']}</td>
            <td>${queue_item['time_touched']}</td>
        </tr>
    % endfor
    </table>

</%def>