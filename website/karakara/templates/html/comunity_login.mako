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
    <% login_providers = data.get('login_providers', {}).items() %>
    % if len(login_providers) == 1:
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
