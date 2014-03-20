<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity</h1>
    
    <ul>
    % for folder in sorted(data.get('folders')):
        <li>${folder}</li>
    % endfor
    <ul>
</%def>
