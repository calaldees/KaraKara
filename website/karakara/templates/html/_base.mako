<!DOCTYPE html>
<html>
    <head>
        <%def name="title()"></%def>
        <title>${self.title()}</title>
        
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, minimum-scale=1.0, maximum-scale=1.0, minimal-ui" />
        
        <!-- CSS Styles -->
        <link   href="${ h.path.external }cssreset-min.css" rel="stylesheet" />
        <link   href="${ h.path.external }jquery.mobile.min.css" rel="stylesheet" />
        <link   href="${ h.path.static   }css/main.css" rel="stylesheet" />
        
        <!-- Scripts -->
        ## TODO: Consider moving js to bottom of page - this may require some refactoring of inline js
        <script src="https://cdnjs.cloudflare.com/ajax/libs/paho-mqtt/1.0.1/mqttws31.min.js" type="text/javascript"></script>
        <script src="${ h.path.static   }js/modernizer.custom.js"></script>
        <script src="${ h.path.external }jquery.min.js"></script>
        <script src="${ h.path.static   }js/jquery.mobile-extras.js"></script>
        <script src="${ h.path.external }jquery.mobile.min.js"></script>
        <script src="${ h.path.external }jquery.cookie.js"></script>
        <script src="${ h.path.external }jquery.sortable.js"></script>
        <script src="${ h.path.static   }js/lib.js"></script>
        <script src="${ h.path.static   }js/karakara.js"></script>
        
        <!-- Other -->
        <link   href="${ h.path.static   }favicon.ico" rel="shortcut icon" />
    </head>
    
    <% body_classs = 'admin' if identity and identity.get('admin',False) else '' %>
    <body class="${body_classs}">
        
        <div data-role="page">
            
            <div data-role="header" data-position="fixed" data-tap-toggle="false">
                <%def name="title()">${request.queue.settings.get('karakara.template.title') or request.registry.settings.get('karakara.template.title') or _('karakara.mobile.template.title.fallback')}</%def>
                <h1>${next.title()}</h1><span id="priority_countdown"></span>
                
                % if request.path != '/':
                ## data-add-back-btn="true" (Could be added to header to auto generate a back button)
                ## ui-btn-icon-notext -> ui-btn-icon-right to get text
                <a href="#" class="ui-btn-icon-notext ui-btn-left  ui-btn ui-btn-inline ui-mini ui-corner-all ui-icon-back" data-rel="back">${_('mobile.base.back')}</a>
                <a href="${paths.get('queue', '/')}" class="ui-btn-icon-notext ui-btn-right ui-btn ui-btn-inline ui-mini ui-corner-all ui-icon-home"                >${_('mobile.base.home')}</a>
                % endif
                
            </div><!-- /header -->
            
            <!-- flash messages -->
            <div class="flash_messages">
            % for message in messages:
            <div class="flash_message ui-bar ui-bar-e status_${status}">
                <p>${message}</p>
                <a href="#" class="flash_remove" data-role="button" data-icon="delete" data-iconpos="notext" onclick="$(this).closest('.flash_message').slideUp(function(){$(this).remove()}); return false;">${_('mobile.base.flash_remove')}</a>
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

<%def name="js_websocket_url()">('https:' == document.location.protocol ? 'wss://' : 'ws://') + location.hostname + '/mqtt'</%def>
