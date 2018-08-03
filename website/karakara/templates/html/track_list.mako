<html>
    <head>
        <title>Tracks All</title>
        <link href="${ h.path.external }cssreset-min.css" rel="stylesheet" media="all"/>
        <link href="${ h.path.static   }css/print_list.css" rel="stylesheet" media="all"/>
    </head>
    
    <body>
        ##<h1>Tracks All</h1>
        <%
            fields = ['id_short'] + request.queue.settings.get('karakara.print_tracks.fields',[])
        %>
        <table>
            <thead>
                <tr>
                % for column in fields:
                    <th>
                        % for n, field in enumerate(column.split("-")):
                            % if n > 0:
                                -
                            % endif
                            ${field}
                        % endfor
                    </th>
                % endfor
                </tr>
            </thead>
            <tbody>
            % for track in data.get('list',[]):
                <tr>\
                % for column in fields:
                    <td class="col_${column}">
                    % for n, field in enumerate(column.split("-")):
                        % if n > 0:
                            -
                        % endif
                        ${track.get(field,'') or h.tag_hireachy(track['tags'], field)}
                    % endfor
                    </td>\
                % endfor
                </tr>
            % endfor
            </tbody>
        </table>
    </body>
</html>
