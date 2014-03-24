<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity</h1>
    
    % if 'facebook_dialog_url' in data:
        <script type="text/javascript">
            window.location = "${data.get('facebook_dialog_url') | n}";
        </script>
        <a href="${data.get('facebook_dialog_url')}">Login with facebook</a>
    % endif
    
    % if not identity.get('comunity'):
        <p>you must authenticate</p>
        <% return %>
    % endif
    
    <% comunity = identity['comunity'] %>
    
    <img src="${comunity.get('avatar')}" alt="avatar" /> ${comunity.get('username')}
    
    % if not comunity.get('approved'):
        <p>awaiting user approval from an admin</p>
    % endif
    
</%def>
