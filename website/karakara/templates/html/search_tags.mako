<%inherit file="_base.mako"/>

<%def name="title()">Search Tracks</%def>

<%
    try   : tag_up1 = data['tags'][-1]
    except: tag_up1 = 'root'
    try   : tag_up2 = data['tags'][-2]
    except: tag_up2 = 'root'
%>


% if data.get('tags'):
    <!-- back -->
    <a href="${request.route_path('search_tags', tags="/".join(data['tags'][0:-1]))}" data-role="button" data-icon="back">Back to ${tag_up2}</a>
% endif

<a href="${request.route_path('search_list', tags="/".join(data['tags']))}" data-role="button" data-icon="arrow-r">View all ${len(data.get('trackids',[]))} ${tag_up1}</a>

<!-- sub tags -->
% for parent_tag in data.get('sub_tags_allowed',[]):
<h2>${parent_tag}</h2>
    <ul data-role="listview" data-inset="true">
    % for tag in [tag for tag in data.get('sub_tags',[]) if tag.get('parent')==parent_tag]:
        <li><a href="${request.route_path('search_tags', tags="/".join(data['tags'] + [tag['full']]))}">${tag['name']} <span class="ui-li-count">${tag['count']}</span></a></li>
    % endfor
    </ul>
% endfor

