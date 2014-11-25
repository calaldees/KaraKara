<%inherit file="_base_comunity.mako"/>

<%!
import os

STATUS_TO_BOOTSTRAP_CLASS_LOOKUP = {
	'black': 'muted',
	'red': 'danger',
	'yellow': 'warning',
	'green': 'success',
}

STATUS_TO_BOOTSTRAP_GLYPH_LOOKUP = {
	'black': 'glyphicon-ban-circle',
	'red': 'glyphicon-remove-sign',
	'yellow': 'glyphicon-exclamation-sign',
	'green': 'glyphicon-ok-sign',
}

%>

<%def name="body()">
	<a href="${request.route_path('comunity_upload', spacer='', format='')}">upload</a>

	% if data.get('unprocessed_media_files'):
	<h2>unprocessed media files</h2>
	<ul>
	% for f in data.get('unprocessed_media_files'):
		<li><a href="${h.media_url(f)}">${f}</a></li>
	% endfor
	</ul>
	% endif

	% if data.get('not_imported'):
	<h2>not imported</h2>
	<ul>
	% for folder in data.get('not_imported'):
		<li>${folder}</li>
	% endfor
	</ul>
	% endif
	
	<% missing_source = set(data.get('missing_source',[])) %>
	<h2>tracks</h2>
	<table class="table table-condensed table-hover">
	% for track in data.get('tracks', []):
		<%
			def row_status(tags):
				return ''

			traffic_light_status = track.get('status', {}).get('status', '')
			traffic_light_class = STATUS_TO_BOOTSTRAP_CLASS_LOOKUP.get(traffic_light_status, '')
		%>
		<tr class="${row_status(track.get('tags',{}))} bg-${traffic_light_class}">
		% if track['source_filename'] in missing_source:
			<td colspan="5">${track['source_filename']}</td>
		% else:
			<td>
				<a href="/track/${track['id']}"><span class="glyphicon glyphicon-phone"></span></a>
			</td>
			<td>
				% for preview, url in h.previews(track):
				<a href="${url}"><span class="glyphicon glyphicon-film"></span></a>
				% endfor
			</td>
			<td>
				<a href="/comunity/track/${track['id']}" class="modal_track_link">${track['source_filename']}</a>
			</td>
			<td>
				<%
					status_details = track.get('status', {}).get('status_details', {})
					num_status = len(status_details)
				%>
				% if status_details:
				<div class="traffic_light text-${traffic_light_class}">
					<span class="glyphicon ${STATUS_TO_BOOTSTRAP_GLYPH_LOOKUP.get(traffic_light_status, '')}"></span>
					% if num_status >= 2:
					<span class="badge">${num_status}</span>
					% endif
					<ul class="traffic_light_content">
					% for status_key, messages in status_details.items():
						% for message in messages:
						<li class="alert alert-${STATUS_TO_BOOTSTRAP_CLASS_LOOKUP.get(status_key, '')}">${message}</li>
						% endfor
					% endfor
					</ul>
				</div>
				% endif
			</td>
		% endif
		</tr>
	% endfor
	</table>
	
	<div id="popup" class="hidden">
		<a href="" onclick="$(this).parent().addClass('hidden'); return false;">close</a>
		<div class="content"></div>
	</div>
</%def>
