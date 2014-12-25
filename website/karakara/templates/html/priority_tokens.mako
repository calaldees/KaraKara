<%inherit file="_base.mako"/>

<% fields = ('id', 'issued', 'used', 'session_owner', 'valid_start', 'valid_end') %>

<table data-role="table" data-mode="columntoggle" id="my-table">
% for field in fields:
    <th>${field}</th>
% endfor
% for priority_token in data['priority_tokens']:
    <tr>
    % for field in fields:
        <td>${priority_token[field]}</td>
    % endfor
    </tr>
% endfor
</table>
