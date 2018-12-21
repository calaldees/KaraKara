This nginx container will take karakara traffic and split it into various
backends (player, media, website). If you want karakara itself to be one
backend of many, you can use a config like this:

```
server {
	listen 0.0.0.0:80;
	server_name  karakara.org.uk www.karakara.org.uk;
	access_log  /data/sites/karakara.org.uk/logs/access.log;
	error_log   /data/sites/karakara.org.uk/logs/error.log;
	root /data/sites/karakara.org.uk/htdocs/;

	location / {
		include proxy_params;
		proxy_pass_header Set-Cookie;
		proxy_pass_header ETag;
		proxy_pass_header If-None-Match;
		proxy_http_version 1.1;
		proxy_redirect http:// $scheme://;
		proxy_read_timeout 600s;
		proxy_set_header Upgrade $http_upgrade;
		proxy_set_header Connection "Upgrade";
		proxy_pass http://127.0.0.1:8820/;
	}
}
```
