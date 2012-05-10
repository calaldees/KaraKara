<%inherit file="_base.mako"/>

<%
    def media_url(file):
        return '/media/%s' % file

    def get_loc(attachment_type):
        return [media_url(attatchment['location']) for attatchment in data['attachments'] if attatchment['type']==attachment_type]
    
    video_files = [
        ('.mp4','mp4'),
        ('.ogv','ogg'),
        ('.mpg','mpg'),
        ('.3gp','3gp'),
    ]
%>

<%def name="title()">${data['title']}</%def>


<!-- video -->
<video poster="${get_loc('image')[0]}" controls>
    % for attachment in data['attachments']:
        % for extension, video_type in video_files:
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
% for image_url in get_loc('image'):
    <img src="${image_url}" />
% endfor
</%doc>