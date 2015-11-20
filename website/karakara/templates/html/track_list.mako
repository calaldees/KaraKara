<html>
    <head>
        <title>Tracks All</title>
        <link href="${ h.path.external }cssreset-min.css" rel="stylesheet" media="all"/>
        <link href="${ h.path.static   }css/print_list.css" rel="stylesheet" media="all"/>
    </head>
    
    <body>
        ##<h1>Tracks All</h1>
        <%
            fields = ['id_short'] + request.registry.settings.get('karakara.print_tracks.fields',[])
        %>
        <table>
            <thead>
                <tr>
                    % for field in fields:
                    <th>${field}</th>
                    % endfor
                </tr>
            </thead>
            <tbody>
        % for track in data.get('list',[]):
<tr>\
                % for field in fields:
<td class="col_${field}">${track.get(field,'') or h.tag_hireachy(track['tags'], field) }</td>\
                % endfor
</tr>
        % endfor
            </tbody>
        </table>
    </body>
</html>
