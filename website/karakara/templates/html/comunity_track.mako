<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h2>${data['track']['source_filename']}</h2>
    
    <form id="form_track" action="" data-track_id="${data['track']['id']}">
        <!-- Video preview -->
        ## Inserted video has class of 'video_placeholder'
        <%namespace file="__video.mako" import="video" />
        ${video(data['track'])}

        <!-- Links to hires videos -->
        % for video_hires, url in h.attachment_locations(data['track'], 'video'):
            <a href="${url}">${h.video_mime_type(video_hires)} ${video_hires['extra_fields'].get('vcodec','unknown')}</a>
        % endfor

        <!-- Tags -->
        <lable class="lable_tag_data" for="tag_data">Tag Data</lable>
        <textarea class="input_tag_data" name="tag_data" data-inital="${data.get('tag_data','').replace('"','\"')}">${data.get('tag_data')}</textarea>

        <!-- Subtiltes -->
        <% subtitle_data = data.get('subtitles', '') %>
        <textarea class="input_subtitle_data" name="subtitles" data-inital="${subtitle_data.replace('"','\"')}">${subtitle_data}</textarea>
        
        <!-- Submit -->
        <input type="submit" name="submit" value="submit"/>
    </form>
</%def>
