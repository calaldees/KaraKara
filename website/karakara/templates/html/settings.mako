<%inherit file="_base.mako"/>

% if 'settings' in data:
    <table data-role="table" data-mode="columntoggle" id="my-table">
        <th>setting</th><th>value</th>
    % for key, value in data['settings'].items():
        <tr><td>${key}</td><td>${value}</td></tr>
    % endfor
    </table>
% endif

% if identity.get('admin', False):
    <form action="" method="PUT">
        <label id="setting_label" for="setting_input"></label>
        <input id="setting_input" name="" value=" -> bool">
        <input type="submit" value="Update setting">
    </form>
    
    <script>
    var $setting_input = $('#setting_input');
    var $setting_label = $('#setting_label');
    $('tr').each(function() {
        $row = $(this);
        var key = $($row.children()[0]).text();
        $row.bind("click", function(){
            console.log(key);
            $setting_input.attr('name' , key);
            $setting_label.text(key);
        });
    });
    </script>
% endif