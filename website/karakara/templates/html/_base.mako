<!DOCTYPE html>
<html>
    <head>
        <%def name="title()"></%def>
        <title>${self.title()}</title>
        
        <meta name="viewport" content="width=device-width, initial-scale=1">
        
        <!-- CSS Styles -->
        <link   href="${h.static_url('styles/yui-3.5.0-cssreset-min.css')}"         rel="stylesheet"     />
        <link   href="${h.static_url('jquery.mobile/jquery.mobile-1.1.1.min.css')}" rel="stylesheet"     />
        <link   href="${h.static_url('styles/main.css')}"                           rel="stylesheet"     />
        
        <!-- Scripts -->
        <script src ="${h.static_url('scripts/modernizer.custom.js')}"                                    ></script>
        <script src ="${h.static_url('jquery/jquery-1.7.1.min.js')}"                                      ></script>
        <script src ="${h.static_url('scripts/jquery.mobile-extras.js')}"                                 ></script>
        <script src ="${h.static_url('jquery.mobile/jquery.mobile-1.1.1.min.js')}"                        ></script>
        
        <!-- Other -->
        <link   href="${h.static_url('favicon.ico')}"                               rel="shortcut icon"  />
    </head>
    
    <body>
        
        <div data-role="page">
            
            <div data-role="header" data-position="fixed" \
                
                % if identity and identity.get('admin',False):
                data-theme="e"
                % endif
>
                <%def name="title()">${h.get_setting('text.title', request) or 'KaraKara'}</%def>
                <h1>${next.title()}</h1>
                
                ## data-iconpos="notext"
                ##<a href="/track_list" data-role="button" data-icon="home"   data-mini="true" data-inline="true">Tracks</a>
                ##<a href="/queue"      data-role="button" data-icon="search" data-mini="true" class="ui-btn-right">Queue</a>
                ##
                % if request.path != '/':
                <a data-role="button" data-role="button "data-icon="back"   data-mini="true"  class="ui-btn-left" data-rel="back">Back</a>
                <a href="/"           data-role="button" data-icon="home"   data-mini="true"  class="ui-btn-right"                >Home</a>
                % endif
                
            </div><!-- /header -->
            
            <!-- flash messages -->
            % for message in messages:
            <div class="flash_message ui-bar ui-bar-e">
                <p class="status_${status}">${message}</p>
                <a href="#" class="flash_remove" data-role="button" data-icon="delete" data-iconpos="notext" onclick="$(this).closest('.flash_message').slideUp(function(){$(this).remove()}); return false;">Remove</a>
            </div>
            % endfor
            <!-- /flash messages -->
            
            <div data-role="content">
                ${next.body()}
            </div><!-- /content -->
        
        </div><!-- /page -->
        
    </body>
</html>
