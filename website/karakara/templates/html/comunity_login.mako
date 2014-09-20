<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Login</h1>

    % if identity.get('user'):
        <% data['redirect_url'] = '/comunity' %>
    % endif

    % if 'redirect_url' in data:
        <script type="text/javascript">
            window.location = "${data.get('redirect_url') | n}";
        </script>
        <a href="${data.get('redirect_url')}">Redirect</a>
    % endif

    % if 'run_js' in data:
        <script type="text/javascript">
            ${data.get('run_js') | n}
        </script>
    % endif
</%def>
