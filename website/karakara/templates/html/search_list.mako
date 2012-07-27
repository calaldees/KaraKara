<%inherit file="_base.mako"/>

<%namespace name="search_tags" file="search_tags.mako" import="search_url"/>

<%def name="title()">Search Tracks</%def>


<a href="${search_url()}" data-role="button" data-icon="back">Back to tag browser</a>

<!-- tracks -->
<h2>Tracks</h2>
<ul data-role="listview" data-inset="true">
% for track in data['tracks']:
    <li>
        <a href="${request.route_path('track', id=track['id'], spacer='', format='')}">
            <%
                try   : img_url = h.media_url([attachment['location'] for attachment in track['attachments'] if attachment['type']=='image'][0])
                except: img_url = None
            %>
            % if img_url:
            <img src="${img_url}" />
            % endif
            ${track['tags'].get('from')} ${track['tags'].get('use')} ${track['tags'].get('title')}
        </a>
    </li>
% endfor
</ul>