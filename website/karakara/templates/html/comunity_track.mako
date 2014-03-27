<%inherit file="_base_comunity.mako"/>

<%def name="body()">
    <h1>Comunity Track</h1>
    <form>
        % for subtitle_filename, subtitle_data in data.get('subtitles', {}).items():
        <lable for="subtitles_${subtitle_filename}">${subtitle_filename}</lable>
        <textarea name="subtitles_${subtitle_filename}">${subtitle_data}</textarea>
        % endfor
    </form>
</%def>
