<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Login</h1>
    
    % if 'facebook_dialog_url' in data:
        <script type="text/javascript">
            window.location = "${data.get('facebook_dialog_url') | n}";
        </script>
        <a href="${data.get('facebook_dialog_url')}">Login with facebook</a>
    % endif

    % if identity.get('comunity'):
        <% comunity_path = '/comunity' %>
        <script type="text/javascript">
            window.location = "${comunity_path}";
        </script>
        <a href="${comunity_path}">Return to comunity portal</a>
    % endif
    
</%def>
