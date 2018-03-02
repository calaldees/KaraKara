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
        <input type="hidden" name="format" value="redirect"/>

        ##<input type="submit" value="new"/>
        <button type="submit" class="btn btn-primary">
            <span class="glyphicon glyphicon-plus" aria-hidden="true"></span>
            ${_('new')}
        </button>
    </form>

    <table class="table table-condensed table-hover">
    % for queue in data.get('queues', []):
        <% paths = h.paths_for_queue(queue['id']) %>
        <tr>
            <td>${queue['id']}</td>
            <td>
                <a href="${paths['queue']}">
                    <button type="button" class="btn btn-default">
                        <span class="glyphicon glyphicon-phone" aria-hidden="true"></span>
                        ${_('mobile')}
                    </button>
                </a>
            </td>
            <td>
                <a href="/static/admin_console.html?queue_id=${queue['id']}">
                    <button type="button" class="btn btn-default">
                        <span class="glyphicon glyphicon-th-large" aria-hidden="true"></span>
                        ${_('admin_console')}
                    </button>
                </a>
            </td>
            <td>
                <a href="${paths['player']}">
                    <button type="button" class="btn btn-default">
                        <span class="glyphicon glyphicon-blackboard" aria-hidden="true"></span>
                        ${_('player')}
                    </button>
                </a>
            </td>
            <td>
                <a href="${paths['track_list']}">
                    <button type="button" class="btn btn-default">
                        <span class="glyphicon glyphicon-print" aria-hidden="true"></span>
                        ${_('track_list')}
                    </button>
                </a>
            </td>
            <td>
                <a href="/comunity/settings/${queue['id']}">
                    <button type="button" class="btn btn-default">
                        <span class="glyphicon glyphicon-cog" aria-hidden="true"></span>
                        ${_('settings')}
                    </button>
                </a>
            </td>
            <td>
                <a href="/static/form_badgenames.html?queue_settings_url=${quote_plus(paths['settings'])}">
                    <button type="button" class="btn btn-default">
                        <span class="glyphicon glyphicon-user" aria-hidden="true"></span>
                        ${_('badgenames')}
                    </button>
                </a>
            </td>
            <td>
                <span class="glyphicon glyphicon-tower" aria-hidden="true"></span>
                ${_('admin')}
                <form action="${paths['admin']}"><input type="text" name="password" placeholder="password" /></form>
            </td>
            <td>
                <a href="?method=delete&format=redirect&queue.id=${queue['id']}">
                    <button type="button" class="btn btn-danger">
                        <span class="glyphicon glyphicon-trash" aria-hidden="true"></span>
                        ${_('delete')}
                    </button>
                </a>
            </td>
        </tr>
    % endfor
    </table>
</%def>
