<%inherit file="_base.mako"/>

<h2>Tracks from Tags</h2>

% for track in data.get('tracks'):
<p>${track.get('title')}:${track.get('duration')}</p>
% endfor