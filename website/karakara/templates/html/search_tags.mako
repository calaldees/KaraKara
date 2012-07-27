<%inherit file="_base.mako"/>

<%def name="title()">Search Tracks</%def>

<%def name="search_url(tags=None,keywords=None,route='search_tags')"><%
        if tags    ==None: tags     = data.get('tags'    ,[])
        if keywords==None: keywords = data.get('keywords',[])
##    def search_url(tags,keywords,route='search_tags'):
        route_path = request.route_path(route, tags="/".join(tags))
        if keywords:
            route_path += '?keywords=%s' % " ".join(keywords) #AllanC - WTF!!! Why do I have to do this HACK to append the query string ... jesus, I don't understand pyramids ***ing url gen and crappy routing ...
        ##return route_path
%>${route_path}</%def>


<%

    #tags     = data.get('tags'    ,[])
    #keywords = data.get('keywords',[])

    try   : tag_up1 = tags[-1]
    except: tag_up1 = 'root'
    #try   : tag_up2 = data['tags'][-2]
    #except: tag_up2 = 'root'
    
%>

% for tag in data['tags']:
    <%
        tags_modifyed = list(data['tags'])
        tags_modifyed.remove(tag)
    %>
    <a href="${search_url(tags=tags_modifyed)}" data-role="button" data-icon="delete">${tag}</a>
% endfor
% for keyword in data['keywords']:
    <%
        keywords_modifyed = list(data['keywords'])
        keywords_modifyed.remove(keyword)
    %>
    <a href="${search_url(keywords=keywords_modifyed)}" data-role="button" data-icon="delete">${keyword}</a>
% endfor

##% if data.get('tags'):    
##    <!-- back -->
##    <a href="${request.route_path('search_tags', tags="/".join(data['tags'][0:-1]))}" data-role="button" data-icon="back">Back to ${tag_up2}</a>
##% endif

<form action="${search_url()}" method="GET">
    <input type="text" name="keywords" placeholder="Add search keywords">
</form>

<a href="${search_url(route='search_list')}" data-role="button" data-icon="arrow-r">List ${len(data.get('trackids',[]))} Tracks</a>

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

