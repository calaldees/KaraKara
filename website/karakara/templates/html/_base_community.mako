<%!
	login_url = '/community/login'
	logout_url = '/community/logout'
%>

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
		${modals()}
		
		<!-- Footer -->
		${self.footer()}
		${scripts()}
	</body>

</html>
</%def>


<%def name="navbar()">

	<nav class="navbar navbar-default navbar-fixed-top" role="navigation">
		<div class="container-fluid">

			<!-- Title + Home -->
			<div class="navbar-header">
				<button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".bs-navbar-collapse">
					<span class="sr-only">Toggle navigation</span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
					<span class="icon-bar"></span>
				</button>

				<!-- Brand Title -->
				<a href="/community" class="navbar-brand">${request.registry.settings.get('community.title', 'KaraKara')}</a>
			</div>

			<div class="collapse navbar-collapse bs-navbar-collapse">
				<ul class="nav navbar-nav">
					##${self.navbar_elements()}
					% if (identity.get('user') or {}).get('approved'):
					<li><a href="/community/list">Tracks</a></li>
					##<li><a href="${request.route_path('community_upload', spacer='', format='')}">upload</a></li>
					##<li><a href="/search_tags/">MobileBrowse</a></li>
					##<li><a href="/track_list">PrintableList</a></li>
					<li><a href="/community/queues">${_('Queues').title()}</a></li>
					##<li><a href="/community/settings">Settings</a></li>
					<li><a href="/community/processmedia_log?levels=WARNING,ERROR">EncodeLog</a></li>
					<li><a href="/community/users">Users</a></li>
					% endif
					##<li class="active"><a href="#">Link</a></li>
				</ul>

				<ul class="nav navbar-nav navbar-right">
				% if identity.get('user'):
					% if not identity['user'].get('approved'):
						<li class="navbar-text label label-warning"><span class="glyphicon glyphicon-warning-sign" data-toggle="tooltip" data-placement="left" title="Awaiting user approval from an admin"></span></li>
					% endif
					<li class="dropdown">
						<% user = identity.get('user') %>
						<a href="#" class="dropdown-toggle" data-toggle="dropdown">
							% if user.get('avatar_url'):
							<img src="${user.get('avatar_url')}" alt="${user.get('username')}" class="avatar"/>
							% endif
							<b class="caret"></b>
						</a>
						<ul class="dropdown-menu">
							<li><a href="${logout_url}">Logout</a></li>
						</ul>
					</li>
				% else:
					<li><a href="${login_url}">Login</a></li>
				% endif
				</ul>
			</div><!-- /.navbar-collapse -->

		</div><!-- /.container-fluid -->
	</nav>
</%def>

<%def name="messagebar()">
	% for message in messages:
	<div class="alert alert-warning">${message}</div>
	% endfor
</%def>

<%def name="head()">
		<!-- Force latest IE rendering engine or ChromeFrame if installed -->
		<!--[if IE]>
		<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
		<![endif]-->

		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
		<meta name="description" content="">
		<meta name="author" content="">
		
		<!-- External CSS -->
		<link href="${h.path.external}css/bootstrap.min.css" rel="stylesheet">
		##<link href="${h.path.external}css/bootstrap-theme.min.css" rel="stylesheet">
		
		<!-- Site CSS -->
		<link href="${h.path.static}css/community.css" rel="stylesheet" />
		
		<!-- Favicons -->
		<link rel="shortcut icon"                                href="${h.path.static}favicon.ico">
</%def>

<%def name="footer()">
	##<%include file="_footer.mako"/>
</%def>

<%def name="scripts()">
	<!-- Javascript -->
	<script src="${h.path.static  }js/modernizer.custom.js"></script>
	<script src="${h.path.external}jquery.min.js"></script>
	<script src="${h.path.external}js/bootstrap.min.js"></script>
	<script src="${h.path.external}jquery.cookie.js"></script>
	<script src="${h.path.external}js/vendor/jquery.ui.widget.js"></script>
	<script src="${h.path.external}js/jquery.iframe-transport.js"></script>
	<script src="${h.path.external}js/jquery.fileupload.js"></script>
	<script src="${h.path.static  }js/community.js"></script>

	<!-- Javascript programatic inline -->
	<%
		js_inlines = h.javascript_inline['community']
		if callable(js_inlines):
			js_inlines = js_inlines(request)
	%>
	% for js_include in js_inlines:
		${js_include |n}
	% endfor

	<!-- Javascript Inline -->
	<script type="text/javascript">
		${next.scripts_inline()}
	</script>
</%def>
<%def name="scripts_inline()"></%def>

<%def name="modals()">
	<!-- Modal - Track -->
	<div class="modal fade" id="modalTrack" tabindex="-1" role="dialog" aria-labelledby="modalProgressLabel" aria-hidden="true">
		<div class="modal-dialog">
			<div class="modal-content">
				<div class="modal-header">
					<button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
				<h4 class="modal-title">Track</h4>
				</div>
				<div class="modal-body">
				</div>
				<div class="modal-footer">
					<button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
					<button type="button" class="btn btn-primary" onclick="$('#modalTrack .modal-body form').submit();">Save changes</button>
				</div>
			</div><!-- /.modal-content -->
		</div><!-- /.modal-dialog -->
	</div><!-- /.modal -->
</%def>
