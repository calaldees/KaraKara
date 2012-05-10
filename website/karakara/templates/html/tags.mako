<%inherit file="_base.mako"/>

<%
    def media_url(file):
        return '/media/%s' % file
%>


% if data['tags']:
    <!-- back -->
    <a href="${request.route_path('tags', tags="/".join(data['tags'][0:-1]))}" data-role="button" data-icon="back">Back</a>
% endif

% if data['tracks']:
    <!-- tracks -->
    <h2>Tracks</h2>
    <ul data-role="listview" data-inset="true">
    % for track in data['tracks']:
        <li>
            <a href="${request.route_path('track', id=track['id'], spacer='', format='')}">
                <%
                    try   : img_url = media_url([attachment['location'] for attachment in track['attachments'] if attachment['type']=='image'][0])
                    except: img_url = None
                %>
                % if img_url:
                <img src="${img_url}" />
                % endif
                ${track.get('title')}
            </a>
        </li>
    % endfor
    </ul>
% endif

% if not data['tracks']:
    <!-- sub tags -->
    <h2>Sub Tags</h2>
    <ul data-role="listview" data-inset="true">
    % for tag in data.get('sub_tags'):
        <li><a href="${request.route_path('tags', tags="/".join(data['tags'] + [tag['name']]))}">${tag['name']} <span class="ui-li-count">${tag['count']}</span></a></li>
    % endfor
    </ul>
% endif