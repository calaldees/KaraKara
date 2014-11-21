<%inherit file="_base_comunity.mako"/>

<%!
import os
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
		%>
		<tr class="${row_status(track.get('tags',{}))}">
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
				% for status_key in {'yellow', 'red'} & track.keys():
				<div class="popover bottom" style="background-color: ${status_key};" data-toggle="popover">
					<div class="arrow"></div>
					<h3 class="popover-title">${status_key}</>
					<div class="popover-content"><ul>
						% for message in track[status_key]:
						<li>${message}</li>
						% endfor
					</ul></div>
				</div>
				% endfor
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
