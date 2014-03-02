<%
	# Example URL
	#   http://localhost/munin/munin-cgi-graph/localdomain/localhost.localdomain/cpu-pinpoint=1393675625,1393783625.png?&lower_limit=&upper_limit=&size_x=800&size_y=400

	import datetime
	from collections import namedtuple
	from externals.lib.misc import epoc, now

	munin_graph_path = '/munin/munin-cgi-graph/localdomain/localhost.localdomain/'
	
	Size = namedtuple('Size', ['x','y'])
	graph_size = Size(400, 200)
	graph_types = (
		'if_eth0',
		'diskstats_iops/sda',
		'diskstats_throughput/sda',
		'cpu',
		'load',
		'memory',
	)
	graph_end = now()
	graph_start = graph_end - datetime.timedelta(hours=2)
%>
<html>
	<head>
	</head>

	<body>
		<h1>Stats</h1>
		% for graph_type in graph_types:
		<img src="${munin_graph_path}${graph_type}-pinpoint=${epoc(graph_start)},${epoc(graph_end)}.png?&lower_limit=&upper_limit=&size_x=${graph_size.x}&size_y=${graph_size.y}" alt="${graph_type}">
		% endfor
	</body>
</html>

