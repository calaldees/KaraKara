<%inherit file="_base_comunity.mako"/>

<%!

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
	<h2>Tracks</h2>

	<p>Filter: <input id="track_filter_input" type="text" name="search" size="50"/></p>
	<script type="text/javascript">{
		const filter_func = (filter_text) => {
			const rows = document.getElementById("track_list").getElementsByTagName("tr");
			for (let row of rows) {
				const tags_string = row.attributes.getNamedItem('data-tags').value;
				row.hidden = tags_string.indexOf(filter_text) < 0;
			}
		};
		const trackFilterInput = document.getElementById("track_filter_input");
		trackFilterInput.addEventListener('keydown', function(event) {
			if (event.keyCode === 13) {
				filter_func(trackFilterInput.value);
			}
		}, true);
	}</script>

	<table id="track_list" class="table table-condensed table-hover">
	% for track in data.get('tracks', []):
		${track_row(track)}
	% endfor
	</table>

	<div id="popup" class="hidden">
		<a href="" onclick="$(this).parent().addClass('hidden'); return false;">close</a>
		<div class="content"></div>
	</div>
</%def>


<%def name="track_row(track)">
	<%
		traffic_light_status = track.get('status', {}).get('status', '')
		traffic_light_class = STATUS_TO_BOOTSTRAP_CLASS_LOOKUP.get(traffic_light_status, '')
	%>
	<tr class="bg-${traffic_light_class}" data-tags="${', '.join(track.get('tags_flattened', []))}">
		<td>
			<a href="/track/${track['id']}"><span class="glyphicon glyphicon-phone"></span></a>
		</td>
		<td>
			% for preview, url in h.attachment_locations(track, 'preview'):
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
	</tr>
</%def>
