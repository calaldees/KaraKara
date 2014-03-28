<html>
    <head>
        <title>Comunity</title>
        
        <link href="${h.static_url('css/comunity.css')}" rel="stylesheet" />
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
        
        <script src ="${h.extneral_url('jquery.min.js')}"></script>
    </body>
</html>
