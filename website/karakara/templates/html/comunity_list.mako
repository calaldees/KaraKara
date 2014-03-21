<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Lists</h1>
    
    % if data.get('not_imported'):
    <h2>not imported</h2>
    <ul>
    % for folder in data.get('not_imported'):
        <li>${folder}</li>
    % endfor
    </ul>
    % endif
    
    <% missing_source = set(data.get('missing_source')) %>
    <h2>tracks</h2>
    <ul>
    % for track in data.get('tracks'):
        % if track['source_filename'] in missing_source:
        <li class="missing">${track['source_filename']}</li>
        % else:
        <li><a href="/track/${track['id']}">${track['source_filename']}</a></li>
        % endif
    % endfor
    <ul>
</%def>
