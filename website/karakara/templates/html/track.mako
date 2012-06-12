<%inherit file="_base.mako"/>

<%

    def media_urls_by_type(attachment_type):
        return [h.media_url(attatchment['location']) for attatchment in data['attachments'] if attatchment['type']==attachment_type]

%>

<%def name="title()">${data['title']}</%def>


<div data-role="collapsible" data-content-theme="c">
    <h3>Queue Track</h3>
    <form action='/queue' method='POST' data-ajax="false">
        <input type='hidden' name='format'         value='redirect'      />
        <input type='text'   name='performer_name' value=''              />
        <input type='hidden' name='track_id'       value='${data['id']}' />
        <input type='submit' name='submit_'        value='Queue Track'   />
    </form>
</div>


<!-- video -->
<video poster="${media_urls_by_type('image')[0]}" controls>
    % for attachment in data['attachments']:
        % for extension, video_type in h.video_files:
            % if extension in attachment['location']:
    <source src="${attachment['location']}" type="video/${video_type}" />
            % endif
        % endfor
    % endfor
    ##<a href="${preview_url}">preview</a>
</video>

<!-- details -->
<p>${data['description']}</p>


<%doc>
<!-- images -->
% for image_url in media_urls_by_type('image'):
    <img src="${image_url}" />
% endfor
</%doc>