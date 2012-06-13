<!DOCTYPE html>
<html>
    <head>
        <%def name="title()"></%def>
        <title>${self.title()}</title>
        
        <meta name="viewport" content="width=device-width, initial-scale=1">
        
        <%
            def static(file):
                #return request.static_url('karakara:static/%s' % file)
                return "/static/"+file
        %>
        
        <!-- CSS Styles -->
        <link   href="${static('styles/yui-3.5.0-cssreset-min.css')}"         rel="stylesheet"     />
        <link   href="${static('jquery.mobile/jquery.mobile-1.1.0.min.css')}" rel="stylesheet"     />
        <link   href="${static('styles/main.css')}"                           rel="stylesheet"     />
        
        <!-- Scripts -->
        <script src ="${static('scripts/jquery-1.7.1.min.js')}"                                     ></script>
        <script src ="${static('scripts/jquery.mobile-extras.js')}"                                 ></script>
        <script src ="${static('jquery.mobile/jquery.mobile-1.1.0.min.js')}"                        ></script>
        
        <!-- Other -->
        <link   href="${static('favicon.ico')}"                               rel="shortcut icon"  />
    </head>
    
    <body> 
        
        <div data-role="page">
            
            <div data-role="header" data-position="fixed" \

                % if identity.get('admin',False):
                data-theme="e"
                % endif
>
                <%def name="title()">${request.registry.settings.get('text.title') or 'KaraKara'}</%def>
                <h1>${next.title()}</h1>
                
                ## data-iconpos="notext"
                <a href="/" data-role="button" data-icon="home"   data-mini="true" data-inline="true">Home  </a>
                <a href="/" data-role="button" data-icon="search" data-mini="true" data-inline="true">Search</a>
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
