<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Track</h1>
    <form action="" onsubmit="track.submit_track(); return false;">
        <lable for="tag_data">Tag Data</lable>
        <textarea name="tag_data" data-inital="${data.get('tag_data').replace('"','\"')}">${data.get('tag_data')}</textarea>
    
        % for subtitle_filename, subtitle_data in data.get('subtitles', {}).items():
        <lable for="subtitles_${subtitle_filename}">${subtitle_filename}</lable>
        <textarea name="subtitles_${subtitle_filename}" data-inital="${subtitle_data.replace('"','\"')}">${subtitle_data}</textarea>
        % endfor
        
        <input type="submit" name="submit" value="submit"/>
    </form>
    
    <script type="text/javascript">
        var track = {
            submit_track: function() {
                // Intercept onsubmit event and ajax submit the form
                    // only post the changed fields
                // on success close popup
            }
        }
    
        $(document).ready(function() {
            
        });
    </script>
</%def>
