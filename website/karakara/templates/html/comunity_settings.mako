<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Settings</h1>

    <form method="POST">
        <ul>
        ##% for k, v in data.get('settings', {}).items():
        % for k in sorted(data.get('settings', {}).keys()):
            <%
                v = data.get('settings', {}).get(k)
                if isinstance(v, list):
                    v = ', '.join(map(str, v))
                v = str(v)
            %>
            <li><label for="input_${k}">${k}</label><input id="input_${k}" type="text" name="${k}" value="${v}" /></li>
        % endfor
        </uL>
        <input type="hidden" name="method" value="PUT">
        <input type="submit" value="Update">
    </form>
</%def>