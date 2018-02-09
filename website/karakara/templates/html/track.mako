<%inherit file="_base.mako"/>

<%def name="title()">${_('mobile.track.title')}</%def>

<%
    track = data.get('track')
    if not track:
        return ''
%>

<h1 class="track_title">${h.track_title_only(track['tags'])}</h1>

<p class="track_code">Track ID: <span>${track['id'][:request.registry.settings.get('karakara.print_tracks.short_id_length', 6)]}</span></p>

<table class="track_tags">
% for key,values in track['tags'].items():
    % if values:
    <tr><th>${key}</th><td>${", ".join(values)}</td></tr>
    % endif
% endfor
</table>

## Video Preview ---------------------------------------------------------------

<%namespace file="__video.mako" import="video" />
${video(track)}

## Details ---------------------------------------------------------------------

<!-- Details -->
<p>${track['description']}</p>


% if track.get('lyrics'):
<!-- Lyrics -->
<h2>Lyrics</h2>
    % for line in track['lyrics'].split('\n'):
        <p>${line}</p>
    % endfor
% endif

## Actions ---------------------------------------------------------------------

<!-- Queue -->
<div class='add-to-queue-box' data-role="collapsible">
    <h3>Queue Track</h3>
    % if not (identity and identity.get('admin',False)) and request.queue.settings.get('karakara.system.user.readonly'):
        <p>Queuing tracks has been disabled</p>
    % else:
        <% queue_status = track.get('queue',{}).get('status') %>
        % if   queue_status == 'THRESHOLD':
        <p>Track is not requestable because it has already been requested and has reached the request limit</p>
        % elif queue_status == 'PLAYED':
        <p>Track already been played recently.</p>
        % elif queue_status == 'PENDING':
        <p>This track has already been queued. Are you sure you want to still request it?</p>
        % endif
        % if queue_status != 'THRESHOLD':
            <form action='${paths['queue_items']}' method='POST' data-ajax="false" onsubmit="store_performer_name();">
                <input type='hidden' name='format'         value='redirect'      />
                <input type='text'   name='performer_name' value=''              id="input_performer_name" placeholder='_('view.track.input.performer_name.default')}' required />
                ## TODO: reimplement this from settings? Need this in api return? - ${request.registry.settings.get('karakara.template.input.performer_name') or
                <input type='hidden' name='track_id'       value='${track['id']}' />
                <input type='submit' name='submit_'        value='Queue Track'   />
            </form>
            <script>
                function store_performer_name(args) {
                    $.cookie('last_performer_name', {value:$("#input_performer_name").val()}, {path:'/'});
                }
                $(document).ready(function() {
                    $('#input_performer_name').val($.cookie("last_performer_name").value || "");
                });
            </script>
        % endif
    % endif
</div>


<!-- Fave -->
<%doc>
% if request.registry.settings.get('karakara.faves.enabled'):
    <% fave = track['id'] in (identity.get('faves',[]) or []) %>
    <form action="/fave.redirect" method="${'DELETE' if fave else 'POST'}">
        % if fave:
        <input type='hidden' name='method' value='delete' />
        % endif
        <input type="hidden" name="id" value="${track['id']}" />
        <input type="submit" value="${'Remove from faves' if fave else 'Add to faves'}" />
    </form>
% endif
</%doc>

##------------------------------------------------------------------------------

% if track.get('queue',{}).get('played'):
<h3>Played</h3>
<ul class="list_played">
% for queue_item in track['queue']['played']:
<li>${queue_item['performer_name']}</li>
% endfor
</ul>
% endif

% if track.get('queue',{}).get('pending'):
<h3>Pending</h3>
<ul class="list_pending">
% for queue_item in track['queue']['pending']:
<li>${queue_item['performer_name']}</li>
% endfor
</ul>
% endif
