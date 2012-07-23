<html>
    <head>
        <title>Tracks All</title>
    </head>
    
    <body>
        <h1>Tracks All</h1>
        
        <%
            fields = ['id','category','from','use','title','artist']
        %>
        
        <table>
            <tr>
                % for field in fields:
                <th>${field}</th>
                % endfor
            </tr>
        % for track in data.get('list',[]):
            <tr>\
                % for field in fields:
<td>${track.get(field) or track['tags'].get(field)}</td>\
                % endfor
</tr>
        % endfor
        </table>
    </body>
</html>