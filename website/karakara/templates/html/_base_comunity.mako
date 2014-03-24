<html>
    <head>
        <title>Comunity</title>
    </head>
    
    <body>
        % for message in messages:
        <p>${message}</p>
        % endfor
        ${next.body()}
    </body>
</html>
