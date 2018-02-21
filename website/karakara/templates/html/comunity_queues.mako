<%inherit file="_base_comunity.mako"/>

<%!
    from urllib.parse import quote_plus
%>


<%def name="body()">
    <h1>Queues</h1>

    <p>INCOMPLETE FEATURE: Even though the foundation for multiple queues are in place. Only ONE queue can be used at a time.</p>

    <form action="" method="POST">
        <label for="input_queue_id">Name</label><input id="input_queue_id" type="text" name="queue_id"/>
        <label for="input_queue_password">Password</label><input id="input_queue_password" type="text" name="queue_password"/>
        <input type="submit" value="new"/>
        <input type="hidden" name="format" value="redirect"/>
    </form>

    <table class="table table-condensed table-hover">
    % for queue in data.get('queues', []):
        <% paths = h.paths_for_queue(queue['id']) %>
        <tr>
            <td>${queue['id']}</td>
            <td><a href="${paths['queue']}">${_('mobile')}</a></td>
            <td><a href="${paths['player']}">${_('player')}</a></td>
            <td><a href="${paths['track_list']}">${_('track_list')}</a></td>
            <td><a href="/comunity/settings/${queue['id']}">${_('settings')}</a></td>
            <td><a href="/static/form_badgenames.html?queue_settings_url=${quote_plus(paths['settings'])}">${_('badgenames')}</a></td>
            <td>${_('admin')} <form action="${paths['admin']}"><input type="text" name="password" placeholder="password"></form></td>
            <td><a href="?method=delete&format=redirect&queue.id=${queue['id']}">${_('delete')}</a></td>
        </tr>
    % endfor
    </table>
</%def>
