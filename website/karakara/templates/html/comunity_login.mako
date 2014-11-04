<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Login</h1>

    % if identity.get('user'):
        <% data['redirect_url'] = '/comunity' %>
    % endif

    % for login_provider_data in data.get('login_providers', {}).values():
        % if 'redirect_url' in data:
            <script type="text/javascript">
                window.location = "${data.get('redirect_url') | n}";
            </script>
            <a href="${data.get('redirect_url')}">Redirect</a>
        % endif
    % endfor
</%def>

<%def name="scripts_inline()">
    % for login_provider_data in data.get('login_providers', {}).values():
        % if 'run_js' in login_provider_data:
            ${login_provider_data.get('run_js') | n}
        % endif
    % endfor
</%def>
