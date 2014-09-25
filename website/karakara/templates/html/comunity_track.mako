<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h2>${data['track']['source_filename']}</h2>
    
    <form id="form_track" action="" data-track_id="${data['track']['id']}">
        <!-- Video preview -->
        ## Inserted video has class of 'video_placeholder'
        <%namespace file="__video.mako" import="video" />
        ${video(data['track'])}

        <!-- Tags -->
        <lable class="lable_tag_data" for="tag_data">Tag Data</lable>
        <textarea class="input_tag_data" name="tag_data" data-inital="${data.get('tag_data','').replace('"','\"')}">${data.get('tag_data')}</textarea>

        <!-- Subtiltes -->
        <div class="panel-group" id="subtitle_accordian">
            % for subtitle_filename, subtitle_data in data.get('subtitles', dict()).items():
            <div class="panel panel-default">
                <lable class="panel-heading lable_subtitle_data" for="subtitles_${subtitle_filename}">
                    <a data-toggle="collapse" data-parent="#subtitle_accordian" href="#subtitle_${loop.index}">
                        ${subtitle_filename}
                    </a>
                </lable>
                <div id="#subtitle_${loop.index}" class="panel-collapse collapse">
                    <div class="panel-body">
                        <textarea class="input_subtitle_data" name="subtitles_${subtitle_filename}" data-inital="${subtitle_data.replace('"','\"')}">${subtitle_data}</textarea>
                    </div>
                </div>
            </div>
            % endfor
        </div>
        
        <!-- Submit -->
        <input type="submit" name="submit" value="submit"/>
    </form>
</%def>
