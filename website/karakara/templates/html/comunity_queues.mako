<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Queues</h1>

    <form action="" method="POST">
        <input type="text" name="id"/>
        <input type="submit" value="new"/>
    </form>

    <ul>
    % for queue in data.get('queue', []):
        <li>
            ${queue['id']}
            <a href="?method=delete&format=redirect&queue.id=${queue['id']}">Delete</a>
        </li>
    % endfor
    </ul>
</%def>
