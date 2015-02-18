<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Settings</h1>
    
    <form method="POST">
        <ul>
        % for k, v in data.get('settings', {}).items():
            <%
                if isinstance(v, list):
                    v = ', '.join(v)
            %>
            <li><label for="input_${k}">${k}</label><input id="input_${k}" type="text" name="${k}" value="${v}" /></li>
        % endfor
        </uL>
        <input type="submit" value="Update">
    </form>
</%def>