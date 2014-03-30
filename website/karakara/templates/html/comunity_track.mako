<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Track</h1>
    <form id="form_track" action="" data-track-id="${data.get('track',{}).get('id','')}">
        ## onsubmit="track.submit_track(); return false;"
        <lable for="tag_data">Tag Data</lable>
        <textarea name="tag_data" data-inital="${data.get('tag_data','').replace('"','\"')}">${data.get('tag_data')}</textarea>
    
        % for subtitle_filename, subtitle_data in data.get('subtitles', {}).items():
        <lable for="subtitles_${subtitle_filename}">${subtitle_filename}</lable>
        <textarea name="subtitles_${subtitle_filename}" data-inital="${subtitle_data.replace('"','\"')}">${subtitle_data}</textarea>
        % endfor
        
        <input type="submit" name="submit" value="submit"/>
    </form>
    
    <script type="text/javascript">
        ##$(document).ready(function() {
        document.addEventListener("DOMContentLoaded", function() {
        
            // Intercept onsubmit event and ajax submit the form
            
            // on success close popup
            $('#form_track').on("submit", function() {
                var $form = $(this);
                var track_id = $form.data().id;
                
                // Only post the changed fields by disbaling the unchanged fields
                $.each($form.find('textarea'), function(index, textarea) {
                    $textarea = $(textarea);
                    console.log($textarea.val(), $textarea.data('inital'));
                    if ($textarea.val() == $textarea.data('inital')) {
                        $textarea.attr('disabled', true);
                    }
                });
                
                var form_data = $form.serialize();
                $.ajax("/comunity/track/"+track_id+".json", {
                    type: "POST",
                    dataType: "json",
                    data: form_data,
                    success: function(data, text, jqXHR) {
                        var response = jqXHR.responseJSON
                        console.log(response);
                    },
                    error: function(jqXHR) {
                        console.error(jqXHR);
                    }
                });
                return false;
            });
            
        });
    </script>
</%def>
