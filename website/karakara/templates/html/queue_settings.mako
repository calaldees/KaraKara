<%inherit file="_base.mako"/>

<%def name="title()">Settings</%def>

<%def name="body()">

    % if 'settings' in data:
        <table data-role="table" data-mode="columntoggle" id="my-table">
            <th>Setting</th><th>Value</th>
        % for key, value in sorted(data['settings'].items()):
            <tr><td>${key}</td><td>${value}</td></tr>
        % endfor
        </table>
    % endif

</%def>