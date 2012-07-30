<%inherit file="_base.mako"/>

<%def name="title()">Track</%def>

<%
    track = data['track']
%>

<h1 class="track_title">${h.track_title_only(track)}</h1>

<table class="track_tags">
% for key,values in track['tags'].items():
    % if values:
    <tr><th>${key}</th><td>${", ".join(values)}</td></tr>
    % endif
% endfor
</table>

## Video Preview ---------------------------------------------------------------

<%
    def previews(track):
        previews = [attachment for attachment in track['attachments'] if attachment['type']=='preview']
        previews = [(preview, h.media_url(preview['location'])) for preview in previews]
        return previews
%>

<!-- html5 - video -->
<div class="html5_video_embed" style="display: none;">
    <video class="video_placeholder" poster="${h.thumbnail_location_from_track(track)}" durationHint="${track['duration']}" controls>
        % for preview, url in previews(track):
            <source src="${url}" type="video/${h.video_mime_type(preview)}" />
            ##<p>${preview['extra_fields'].get('vcodec','unknown')}</p>
        % endfor
        <%doc>
            % for extension, video_type in h.video_files:
                % if extension in attachment['location']:
                % endif
            % endfor
        </%doc>
    </video>
</div>

<!-- non html5 - video link & thumbnail carousel -->
<div class="html5_video_link">
    <!-- thumbnails -->
    <div class="thumbnails">
    % for thumbnail_url in h.attachment_locations_by_type(track,'thumbnail'):
        <img src="${thumbnail_url}" class="video_placeholder" style="display: none;"/>
    % endfor
    </div>
    
    ## Cycle the images as a carousel (custom carousel via plain hide/show)
    <script type="text/javascript">
        var current_thumbnail;
        cycleThumbnail();
        function cycleThumbnail() {
            
            if (current_thumbnail) {
                current_thumbnail.hide();
                current_thumbnail = current_thumbnail.next();
            }
            if (current_thumbnail==null || current_thumbnail.length==0) {
                current_thumbnail = $('.thumbnails').children('img:first');
            }
            if (current_thumbnail) {
                current_thumbnail.show();
            }
        }

        ## AllanC - currently the only form of video being generated by the mediaprocess is h264. In the future this could be changed to use the plain css selectors, for now this is sufficent.
        $(function() {
            if (Modernizr.video.h264 && !isWebOS()) { //HACK for isWebOS, webos incorrectly responds with 'probably'
                $('.html5_video_embed').show(); // Show html5 video element
                $('.html5_video_link' ).hide(); // Hide the static video link
            }
            else {
                interval_id = setInterval(cycleThumbnail, 3000); // Star the coursel for the staic images
            }
        });
    </script>
    
    % for preview, url in previews(track):
    <a href="${url}" data-role="button" rel=external target="_blank">Preview Video</a>
    ## ${preview['extra_fields'].get('target','unknown')}
    % endfor
</div>

## Details ---------------------------------------------------------------------

<!-- Details -->
<p>${track['description']}</p>


<!-- Lyrics -->
<h2>Lyrics</h2>
% for lyrics in track['lyrics']:
    ##${lyrics['language']}
    % for line in lyrics['content'].split('\n'):
        <p>${line}</p>
    % endfor
% endfor

## Actions ---------------------------------------------------------------------

<!-- Queue -->
<div data-role="collapsible" data-content-theme="c">
    <h3>Queue Track</h3>
    <form action='/queue' method='POST' data-ajax="false">
        <input type='hidden' name='format'         value='redirect'      />
        <input type='text'   name='performer_name' value=''              placeholder='Enter your name' required />
        <input type='hidden' name='track_id'       value='${track['id']}' />
        <input type='submit' name='submit_'        value='Queue Track'   />
    </form>
</div>

<!-- Fave -->
<% fave = track['id'] in identity.get('faves',[]) %>
<form action="/fave.redirect" method="${'DELETE' if fave else 'POST'}">
    % if fave:
    <input type='hidden' name='method' value='delete' />
    % endif
    <input type="hidden" name="id" value="${track['id']}" />
    <input type="submit" value="${'Remove from faves' if fave else 'Add to faves'}" />
</form>

##------------------------------------------------------------------------------

% if 'queued' in track:
<h3>Queued by</h3>
<ul>
% for queue_item in track['queued']:
<li>${queue_item['performer_name']}</li>
% endfor
</ul>
% endif