<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Settings</h1>

    <form method="POST">
        <table>
            <%
                last_section = ""
            %>
            % for k in sorted(data.get('settings', {}).keys()):
                <%
                    section = k.split(".")[1]
                    label = ".".join(k.split(".")[2:])
                %>
                % if section != last_section:
                    <tr><th colspan="2"><h2>${section}</h2></th></tr>
                    <%
                        last_section = section
                    %>
                % endif

                <%
                    v = data.get('settings', {}).get(k)
                    if isinstance(v, list):
                        v = f"""[{', '.join(map(str, v))}]"""
                    v = str(v)
                %>
                <tr>
                    <td><label for="input_${k}">${label}</label></td>
                    <td><input id="input_${k}" type="text" name="${k}" value="${v}" /></td>
                </tr>
            % endfor
            <tr>
                <td colspan="2">
                    <input type="hidden" name="method" value="PUT">
                    <input type="submit" value="Update">
                </td>
            </tr>
        </table>
    </form>
</%def>