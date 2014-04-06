<%def name="title()"></%def>

<%def name="body()">
% if format == 'html_template':
    ${next.body()} <% return %>
% endif
<!DOCTYPE html>
<html lang="en">

	<head>
		<title>${self.title()}</title>
		${head()}
	</head>

	<body>
		<a class="sr-only" href="#content">Skip navigation</a>
		<!-- Navigation -->
		${navbar()}
        ${messagebar()}
        
		<!-- Content -->
		<div class="container body_container">
			<div class="row">
				<a id="top-ancor"></a>
				${next.body()}
			</div>
		</div>
		
		<!-- Modal dialogs -->
		##${modals()}
		
		<!-- Footer -->
		${self.footer()}
		${scripts()}
	</body>

</html>
</%def>


<%def name="navbar()">
    <%doc>
        % if identity.get('comunity'):
        <% comunity = identity.get('comunity') %>
        <p><img src="${comunity.get('avatar')}" alt="avatar" /> ${comunity.get('username')}</p>
        % endif
    </%doc>

		<header class="navbar navbar-inverse navbar-fixed-top bs-docs-nav" role="banner">
			<div class="container">
				<!-- Top Button -->
				<a href="#top-ancor" class="visible-xs visible-sm fl-nav-goto-top"><span class="glyphicon glyphicon-eject"></span><span class="hidden">Top</span></a>
				
				<!-- Title + Home -->
				<div class="navbar-header">
					<button class="navbar-toggle" type="button" data-toggle="collapse" data-target=".bs-navbar-collapse">
						<span class="sr-only">Toggle navigation</span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>
						<span class="icon-bar"></span>
					</button>
					<!-- Brand Title -->
					<a href="/comunity" class="navbar-brand">${request.registry.settings.get('comunity.title', 'KaraKara')}</a>
                    <%doc>
					<!-- Status Identifyers -->
					<div id="navbar-status">
						<span id="status-offline" class="hidden">                           <span class="glyphicon glyphicon-open" data-toggle="tooltip" placement="bottom" title="Offline mode"></span>       </span>
						<span id="status-extra"                 ><span class="extra_toggle"><span class="glyphicon glyphicon-star" data-toggle="tooltip" placement="bottom" title="Extra content"></span></span></span>
					</div>
                    </%doc>
				</div>
				
				<nav class="collapse navbar-collapse bs-navbar-collapse" role="navigation">
					<ul class="nav navbar-nav">
						##${self.navbar_elements()}
                        <li>About</li>
					</ul>
				</nav>
				
			</div>
		</header>
</%def>

<%def name="messagebar()">
    % for message in messages:
    <p>${message}</p>
    % endfor
</%def>

<%def name="head()">
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
		<meta name="description" content="">
		<meta name="author" content="">
		
		<!-- External CSS -->
		<link href="${h.path.external}css/bootstrap.min.css"       rel="stylesheet">
		##<link href="${h.path.external}css/bootstrap-theme.min.css" rel="stylesheet">
		
		<!-- Site CSS -->
        <link href="${h.path.static}css/comunity.css" rel="stylesheet" />
		
		<!-- Favicons -->
		<link rel="apple-touch-icon-precomposed" sizes="144x144" href="${h.path.static}ico/apple-touch-icon-144-precomposed.png">
		<link rel="apple-touch-icon-precomposed" sizes="114x114" href="${h.path.static}ico/apple-touch-icon-114-precomposed.png">
		<link rel="apple-touch-icon-precomposed" sizes="72x72"   href="${h.path.static}ico/apple-touch-icon-72-precomposed.png">
		<link rel="apple-touch-icon-precomposed"                 href="${h.path.static}ico/apple-touch-icon-57-precomposed.png">
		<link rel="shortcut icon"                                href="${h.path.static}ico/favicon.png">
</%def>

<%def name="footer()">
	##<%include file="_footer.mako"/>
</%def>

<%def name="scripts()">
	<!-- Javascript -->
	<script src="${h.path.external}jquery.min.js"></script>
	<script src="${h.path.external}js/bootstrap.min.js"></script>
	<script src="${h.path.static  }js/comunity.js"></script>
</%def>

<%def name="modals()">
	<!-- Modal - Progress Bar -->
	<div class="modal fade" id="modalProgress" tabindex="-1" role="dialog" aria-labelledby="modalProgressLabel" aria-hidden="true">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
				<h4 class="modal-title">Updating Offline Content</h4>
				</div>
				<div class="modal-body">
					
					<div class="progress">
						<div id="progress-bar" class="progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">
							<span class="sr-only"></span>
						</div>
					</div>
					
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
					##<button type="button" class="btn btn-primary">Save changes</button>
				</div>
			</div><!-- /.modal-content -->
		</div><!-- /.modal-dialog -->
	</div><!-- /.modal -->
</%def>



<%doc>
<html>
    <head>
        <title>Comunity</title>
        
        
    </head>
    
    <body>
        
        ${next.body()}
        
        <script src ="${h.extneral_url('jquery.min.js')}"></script>
        <script src ="${h.static_url('js/comunity.js')}"></script>
    </body>
</html>
</%doc>
