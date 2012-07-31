<%inherit file="_base.mako"/>

<%namespace name="search_tags" file="search_tags.mako" import="search_url"/>

<%def name="title()">Track List</%def>

<!-- tracks -->
<h2>Tracks</h2>
<ul data-role="listview" data-inset="true">
% for track in data['tracks']:
    <li>
        <a href="${request.route_path('track', id=track['id'], spacer='', format='')}">
            <%
                #try   :
                    img_url = h.media_url(track['image']) #[attachment['location'] for attachment in track['attachments'] if attachment['type']=='image'][0]
                #except:
                #    img_url = None
            %>
            % if img_url:
            <img src="${img_url}" />
            % endif
            ${h.track_title(track['tags'], exclude_tags=data['tags'])}
        </a>
    </li>
% endfor
</ul>