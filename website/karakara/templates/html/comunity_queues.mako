<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Queues</h1>

    <p>INCOMPLETE FEATURE: Even though the foundation for multiple queues are in place. Only ONE queue can be used at a time.</p>

    <form action="" method="POST">
        <label for="input_queue_id">Name</label><input id="input_queue_id" type="text" name="queue_id"/>
        <label for="input_queue_password">Password</label><input id="input_queue_password" type="text" name="queue_password"/>
        <input type="submit" value="new"/>
        <input type="hidden" name="format" value="redirect"/>
    </form>

    <ul>
    % for queue in data.get('queues', []):
        <li>
            ${queue['id']}
            <a href="/comunity/settings/${queue['id']}">Settings</a>
            <a href="?method=delete&format=redirect&queue.id=${queue['id']}">Delete</a>
        </li>
    % endfor
    </ul>
</%def>
