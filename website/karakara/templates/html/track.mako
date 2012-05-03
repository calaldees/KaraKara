<%inherit file="_base.mako"/>

<h2>Track</h2>
% for key,value in data.items():
<p>${key}:${value}</p>
% endfor
##from . import DBSession