<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Login</h1>

    % if identity.get('user'):
        <% data['redirect_url'] = '/comunity' %>
    % endif

    <ul class="login_providers">
    % for login_provider_name, login_provider_data in data.get('login_providers', {}).items():
        <li class="${login_provider_name}">
            % if login_provider_data.get('redirect_url'):
            <a href="${login_provider_data.get('redirect_url')}">${login_provider_name}</a>
            % endif
            % if login_provider_data.get('run_js'):
            <a href="#" onclick="${login_provider_data.get('run_js') | n}">${login_provider_name}</a>
            % endif
        </li>
    % endfor
    </ul>
</%def>

<%def name="scripts_inline()">
    ## If there is only one registered provider, we can optionally automatically activate this process.
    ## Note: Some providers require their javascript to be activated via a click action and this could fail.
    ##       check to see if your provider supports this and set login.automatically_activate_with_single_provider to True
    <% login_providers = data.get('login_providers', {}).items() %>
    % if len(login_providers) == 1 and request.registry.settings.get('login.automatically_activate_with_single_provider'):
        % for login_provider_name, login_provider_data in login_providers:
            % if 'run_js' in login_provider_data:
                ${login_provider_data.get('run_js') | n}
            % endif
            % if 'redirect_url' in login_provider_data:
                window.location = "${login_provider_data.get('redirect_url') | n}";
            % endif
        % endfor
    % endif
</%def>
