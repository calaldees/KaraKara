<%inherit file="_base.mako"/>

<%def name="title()">Feedback</%def>

% if 'feedback' in data:
    ## If admin, display feedback
    <ul>
    % for feedback in data['feedback']:
        <li>
            <h3>${feedback['contact']}</h3>
            <p>${feedback['timestamp']}</p>
            <p>${feedback['details']}</p>
        </li>
    % endfor
    </ul>
% else:
    ## If normal user, display feedback form
    <% readonly_field = 'readonly="True"' if request.params.get('details','') else '' %>
    <form action="" method="POST">
        <input    type="text" name="contact" ${readonly_field} value="${request.params.get('contact','')}" placeholder="(optional) email or name"/>
        <textarea             name="details" ${readonly_field}                                             placeholder="What do you think? Got a problem? (what were you doing, what did you expect to happen, what did happen)" rows="6" style="height: auto;">${request.params.get('details','')}</textarea>
        % if not readonly_field:
        <input type="submit" name="submit"  value      ="Submit" />
        % endif
    </form>
% endif
