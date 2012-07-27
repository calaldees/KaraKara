<%inherit file="_base.mako"/>

<%def name="title()">Search Tracks</%def>

<%
    def search_url(tags,keywords,route='search_tags'):
        return request.route_path(route, tags="/".join(tags), keywords=",".join(keywords))

    tags     = data.get('tags'    ,[])
    keywords = data.get('keywords',[])

    try   : tag_up1 = tags[-1]
    except: tag_up1 = 'root'
    #try   : tag_up2 = data['tags'][-2]
    #except: tag_up2 = 'root'
    
%>

% for tag in tags:
    <%
        tags_modifyed = list(data.get('tags'))
        tags_modifyed.remove(tag)
    %>
    <a href="${search_url(tags_modifyed,keywords)}" data-role="button" data-icon="delete">${tag}</a>
% endfor
% for keyword in keywords:
    <%
        keywords_modifyed = list(keywords)
        keywords_modifyed.remove(keyword)
    %>
    <a href="${search_url(tags,keywords_modifyed)}" data-role="button" data-icon="delete">${keyword}</a>
% endfor

##% if data.get('tags'):    
##    <!-- back -->
##    <a href="${request.route_path('search_tags', tags="/".join(data['tags'][0:-1]))}" data-role="button" data-icon="back">Back to ${tag_up2}</a>
##% endif

<form action="${search_url(tags,keywords)}" method="GET">
    <input type="text" name="keywords" placeholder="Add search keywords">
</form>

<a href="${search_url(tags,keywords,route='search_list')}" data-role="button" data-icon="arrow-r">List ${len(data.get('trackids',[]))} Tracks</a>

<!-- sub tags -->
% for parent_tag in data.get('sub_tags_allowed',[]):
<h2>${parent_tag}</h2>
    <ul data-role="listview" data-inset="true">
    <%
        tags = data.get('sub_tags',[])
        show_dividers = True if len(tags) > 10 else False
        previous_tag = {'name':'^'} # an uncommon chacter to be differnt from first character to trigger first divider
    %>
    % for tag in [tag for tag in tags if tag.get('parent')==parent_tag]:
        <%
            new_heading = ''
            try:
                new_heading = tag['name'][0] if previous_tag['name'][0] != tag['name'][0] else ''
            except:
                pass
        %>
        % if show_dividers and new_heading and False:
	<li data-role="list-divider">${new_heading}</li>
        ##<div data-role="collapsible" data-collapsed="true">
        % endif 
        <li><a href="${request.route_path('search_tags', tags="/".join(data['tags'] + [tag['full']]))}">${tag['name']} <span class="ui-li-count">${tag['count']}</span></a></li>
        <% previous_tag = tag %>
    % endfor
    </ul>
% endfor

