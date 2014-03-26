<html>
    <head>
        <title>Comunity</title>
    </head>
    
    <body>
        % for message in messages:
        <p>${message}</p>
        % endfor
        
        % if identity.get('comunity'):
        <% comunity = identity.get('comunity') %>
        <p><img src="${comunity.get('avatar')}" alt="avatar" /> ${comunity.get('username')}</p>
        % endif
        
        ${next.body()}
    </body>
</html>
