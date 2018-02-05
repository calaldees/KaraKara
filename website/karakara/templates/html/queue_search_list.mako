<%inherit file="_base.mako"/>

<%namespace name="search_tags" file="queue_search_tags.mako" import="search_url"/>

<%def name="title()">${_('mobile.search_list.title')}</%def>

<!-- tracks -->
<h2>${_('mobile.search_list.heading')}</h2>
<ul data-role="listview" data-inset="true" class="title">
% for track in data['tracks']:
    <li>
        <a href="${paths['track']}/${track['id']}">
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
