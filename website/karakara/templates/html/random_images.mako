<html>
	<head>
		<title>Random Images</title>
	</head>
	
	<body>
		% for image_url in data.get('images',[]):
		<img src="${image_url}">
		% endfor
	</body>
</html>