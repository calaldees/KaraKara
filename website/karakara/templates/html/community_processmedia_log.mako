<%inherit file="_base_community.mako"/>

<%def name="body()">
	<h2>processmedia2 logs</h2>
	<table class="table table-condensed table-hover">

    <%
        HEADINGS = ('datetime', 'source', 'message')
        LOGLEVEL_TO_BOOTSTRAP_CLASS_LOOKUP = {
            'ERROR': 'danger',
            'WARNING': 'warning',
        }
    %>
    <tr>
    % for heading in HEADINGS:
        <th>${heading}</th>
    % endfor
    </tr>
    
	% for item in reversed(data.get('processmedia_log', [])):
		<tr class="bg-${LOGLEVEL_TO_BOOTSTRAP_CLASS_LOOKUP.get(item.get('loglevel'))}">
            % for heading in HEADINGS:
            <td>${item.get(heading, '').replace('\\n', '<br>') | n}</td>
            % endfor
        </tr>
    % endfor

</%def>