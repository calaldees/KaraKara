This nginx container will take karakara traffic and split it into various
backends (player, media, website). If you want karakara itself to be one
backend of many, you can use a config like this:

```
server {
	listen 0.0.0.0:80;
	server_name  karakara.uk www.karakara.uk;
	access_log  /data/sites/karakara.uk/logs/access.log;
	error_log   /data/sites/karakara.uk/logs/error.log;
	root /data/sites/karakara.uk/htdocs/;

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

References
----------

* [Rotating nginx logs using Docker Compose and logrotate](https://alexanderzeitler.com/articles/rotating-nginx-logs-with-docker-compose/)
	* this is `logrotate` on the host
* [StackOverflow: Logrotate - nginx logs not rotating inside docker container](https://stackoverflow.com/a/46365627/3356840)
	* run CMD to run `cron`->`logrotate` inside `nginx` container
