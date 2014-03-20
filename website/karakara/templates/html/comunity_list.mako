<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Lists</h1>
    
    <ul>
    % for track in data.get('tracks'):
        <li>${track['source_filename']}</li>
    % endfor
    <ul>
</%def>
