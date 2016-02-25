<%inherit file="_base.mako"/>

% if 'settings' in data:
    <table data-role="table" data-mode="columntoggle" id="my-table">
        <th>Setting</th><th>Value</th>
    % for key, value in sorted(data['settings'].items()):
        <tr><td>${key}</td><td>${value}</td></tr>
    % endfor
    </table>
% endif

% if identity.get('admin', False):
    <form action="" method="POST">
        <label id="setting_label" for="setting_input"></label>
        <input id="setting_input" name="" value=" -> bool">
        <input type="hidden" name="method" value="PUT">
        <input type="submit" value="Update setting">
    </form>
    
    <script>
    var $setting_input = $('#setting_input');
    var $setting_label = $('#setting_label');
    $('tr').each(function() {
        $row = $(this);
        var key = $($row.children()[0]).text();
        var value = $($row.children()[1]).text();
        $row.bind("click", function(){
            console.log(key);
            $setting_input.attr('name' , key);
            $setting_input.attr('value' , value);
            $setting_label.text(key);
        });
    });
    </script>
    
    <div data-role="collapsible">
        <h3>Quick Settings</h3>
        
        <%def name="quick_setting(title, key, value)">
            <form action="" method="POST">
                <input type="hidden" name="method" value="PUT">
                <input type="hidden" name="${key}" value="${value}">
                <input type="submit" value="${title}">
            </form>
        </%def>
        
        ${quick_setting('Readonly Mobile Interface', 'karakara.system.user.readonly' , 'True -> bool')}
        ${quick_setting('Disable Mobile Interface' , 'karakara.template.menu.disable', 'Appolgies. The mobile interface has been disabled.')}
        ${quick_setting('Reload Badgenames' , 'karakara.queue.add.valid_performer_names', 'badgenames.txt -> listfile')}
        
    </div>

% endif
