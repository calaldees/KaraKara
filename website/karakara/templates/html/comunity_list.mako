<%inherit file="_base_comunity.mako"/>

<%def name="body()">
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
	<table class="table table-condensed">
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
				<a href="/track/${track['id']}"><span class="glyphicon glyphicon-phone"></a>
			</td>
			<td>
				% for preview, url in h.previews(track):
				<a href="${url}"><span class="glyphicon glyphicon-film"></span></a>
				% endfor
			</td>
			<td>
				<a href="/comunity/track/${track['id']}" class="track_popup">${track['source_filename']}</a>
			</td>
			<%
				tags_display = (
					('title', None),
					('artist', None),  # more relevent for some categorys
					('category', None),
					('lang', None),
					('from', None),  # only relevent for some categorys
					('broken', None),
				)
			%>
			% for tag, tag_icon in tags_display:
			<td>
				${track.get('tags',{}).get(tag)}
			</td>
			% endfor
		% endif
		</tr>
	% endfor
	</table>
	
	<div id="popup" class="hidden">
		<a href="" onclick="$(this).parent().addClass('hidden'); return false;">close</a>
		<div class="content"></div>
	</div>
</%def>
