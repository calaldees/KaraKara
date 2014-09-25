<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h2>${data['track']['source_filename']}</h2>
    
    <form id="form_track" action="" data-track_id="${data['track']['id']}">
        <!-- Video preview -->
        ## Inserted video has class of 'video_placeholder'
        <%namespace file="__video.mako" import="video" />
        ${video(data['track'])}

        <!-- Tags -->
        <lable for="tag_data">Tag Data</lable>
        <textarea name="tag_data" data-inital="${data.get('tag_data','').replace('"','\"')}">${data.get('tag_data')}</textarea>

        <!-- Subtiltes -->
        % for subtitle_filename, subtitle_data in data.get('subtitles', dict()).items():
        <lable for="subtitles_${subtitle_filename}">${subtitle_filename}</lable>
        <textarea name="subtitles_${subtitle_filename}" data-inital="${subtitle_data.replace('"','\"')}">${subtitle_data}</textarea>
        % endfor
        
        <!-- Submit -->
        <input type="submit" name="submit" value="submit"/>
    </form>
</%def>
