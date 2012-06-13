<%inherit file="_base.mako"/>


<%def name="title()">${data['title']}</%def>


<div data-role="collapsible" data-content-theme="c">
    <h3>Queue Track</h3>
    <form action='/queue' method='POST' data-ajax="false">
        <input type='hidden' name='format'         value='redirect'      />
        <input type='text'   name='performer_name' value=''              placeholder='Enter your name' required />
        <input type='hidden' name='track_id'       value='${data['id']}' />
        <input type='submit' name='submit_'        value='Queue Track'   />
    </form>
</div>


<!-- video -->
<video poster="${h.thumbnail_location_from_track(data)}" durationHint="${data['duration']}" controls>
    % for preview in [attachment for attachment in data['attachments'] if attachment['type']=='preview']:
        <% url = h.media_url(preview['location']) %>
        <source src="${url}" type="video/${h.video_mime_type(preview)}" />
        <a href="${url}">${preview['extra_fields'].get('target','unknown')}</a>
        ##<p>${preview['extra_fields'].get('vcodec','unknown')}</p>
    % endfor
    <%doc>
        ##% for extension, video_type in h.video_files:
            ##% if extension in attachment['location']:
            ##% endif
        ##% endfor
    </%doc>
</video>

<!-- details -->
<p>${data['description']}</p>



<!-- thumbnails -->
% for thumbnail_url in h.attachment_locations_by_type(data,'thumbnail'):
    <img src="${thumbnail_url}" />
% endfor

<!-- lyrics -->
% for lyrics in data['lyrics']:
    <h3>${lyrics['language']}</h3>
    % for line in lyrics['content'].split('\n'):
${line}<br/>
    % endfor
% endfor
