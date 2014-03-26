<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity</h1>
    
    % if not identity.get('comunity'):
        <p><a href="/comunity/login">Login</a></p>
    % else:
        <p><a href="/comunity/logout">Logout</a></p>
        
        % if not identity.get('comunity',{}).get('approved'):
            <p>awaiting user approval from an admin</p>
        % else:
           <p>comunity ready</p>
            <a href="/comunity/list">List</a>
        % endif

    % endif

</%def>
