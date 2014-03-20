<!DOCTYPE html>
<html>
    <head>
        <%def name="title()"></%def>
        <title>${self.title()}</title>
        
        <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1.0, maximum-scale=1.0, minimal-ui" />
        
        <!-- CSS Styles -->
        <link   href="${h.extneral_url('cssreset-min.css')}" rel="stylesheet" />
        <link   href="${h.extneral_url('jquery.mobile.min.css')}" rel="stylesheet" />
        <link   href="${h.static_url('css/main.css')}" rel="stylesheet" />
        
        <!-- Scripts -->
        ## TODO: Consider moving js to bottom of page - this may require some refactoring of inline js
        <script src ="${h.static_url('js/modernizer.custom.js')}"></script>
        <script src ="${h.extneral_url('jquery.min.js')}"></script>
        <script src ="${h.static_url('js/jquery.mobile-extras.js')}"></script>
        <script src ="${h.extneral_url('jquery.mobile.min.js')}"></script>
        <script src ="${h.extneral_url('jquery.cookie.js')}"></script>
        <script src ="${h.static_url('js/lib.js')}"></script>
        <script src ="${h.static_url('js/karakara.js')}"></script>
        
        <!-- Other -->
        <link   href="${h.static_url('favicon.ico')}" rel="shortcut icon" />
    </head>
    
    <% body_classs = 'admin' if identity and identity.get('admin',False) else '' %>
    <body class="${body_classs}">
        
        <div data-role="page">
            
            <div data-role="header" data-position="fixed" data-tap-toggle="false">
                <%def name="title()">${request.registry.settings.get('karakara.template.title') or 'KaraKara'}</%def>
                <h1>${next.title()}</h1><span id="priority_countdown"></span>
                
                % if request.path != '/':
                ## data-add-back-btn="true" (Could be added to header to auto generate a back button)
                ## ui-btn-icon-notext -> ui-btn-icon-right to get text
                <a href="#" class="ui-btn-icon-notext ui-btn-left  ui-btn ui-btn-inline ui-mini ui-corner-all ui-icon-back" data-rel="back">Back</a>
                <a href="/" class="ui-btn-icon-notext ui-btn-right ui-btn ui-btn-inline ui-mini ui-corner-all ui-icon-home"                >Home</a>
                % endif
                
            </div><!-- /header -->
            
            <!-- flash messages -->
            <div class="flash_messages">
            % for message in messages:
            <div class="flash_message ui-bar ui-bar-e status_${status}">
                <p>${message}</p>
                <a href="#" class="flash_remove" data-role="button" data-icon="delete" data-iconpos="notext" onclick="$(this).closest('.flash_message').slideUp(function(){$(this).remove()}); return false;">Remove</a>
            </div>
            % endfor
            </div>
            <!-- /flash messages -->
            
            <div data-role="content">
                ${next.body()}
            </div><!-- /content -->
        
        </div><!-- /page -->
        
    </body>
</html>
