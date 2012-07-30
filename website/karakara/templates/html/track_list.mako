<html>
    <head>
        <title>Tracks All</title>
        <link href="${h.static_url('styles/yui-3.5.0-cssreset-min.css')}" rel="stylesheet" media="all"/>
        <link href="${h.static_url('styles/print_list.css')}"             rel="stylesheet" media="all"/>
    </head>
    
    <body>
        ##<h1>Tracks All</h1>
        <%
            fields = ['id','category','from','use','title','artist']
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
<td class="col_${field}">${track.get(field,'') or ", ".join(track['tags'].get(field,[])) }</td>\
                % endfor
</tr>
        % endfor
            </tbody>
        </table>
    </body>
</html>