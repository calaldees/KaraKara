<%inherit file="_base.mako"/>

<table data-role="table" data-mode="columntoggle" id="my-table">
    <th>setting</th><th>value</th>
% for key, value in data['settings'].items():
    <tr><td>${key}</td><td>${value}</td></tr>
% endfor
</table>