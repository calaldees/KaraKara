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
        <div class="panel-group" id="subtitle_accordian" role="tablist" aria-multiselectable="true">
            <%doc>
                Tempory disable this section. To be reimplemented
            <%
                subtitle_filename, subtitle_data = data.get('subtitles', ('', ''))
            %>
            <div class="panel panel-default">
                <div id="subtitle_heading_${loop.index}" class="panel-heading lable_subtitle_data" role="tab">
                    <h4 class="panel-title">
                        <a data-toggle="collapse" data-parent="#subtitle_accordian" href="#subtitle_${loop.index}" aria-expanded="true" aria-controls="subtitle_${loop.index}">
                            ${subtitle_filename}
                        </a>
                    </h4>
                </div>
                <div id="subtitle_${loop.index}" class="panel-collapse collapse" role="tabpanel" aria-labelledby="subtitle_heading_${loop.index}">
                    <div class="panel-body">
                        <textarea class="input_subtitle_data" name="subtitles_${subtitle_filename}" data-inital="${subtitle_data.replace('"','\"')}">${subtitle_data}</textarea>
                    </div>
                </div>
            </div>
            </%doc>
        </div>

        % for video_hires, url in h.attachment_locations(data['track'], 'video'):
            <a href="${url}">${h.video_mime_type(video_hires)} ${video_hires['extra_fields'].get('vcodec','unknown')}</a>
        % endfor
        
        <!-- Submit -->
        <input type="submit" name="submit" value="submit"/>
    </form>
</%def>
