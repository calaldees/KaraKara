KaraKara Websocket Server
=========================
A simple pub/sub server for broadcasting "playlist updated" events to KaraKara clients

More docs: TODO

Subscribers:
------------
Connect to `ws://host:port/channel_name.ws`

Publishers:
-----------
```
GET /channel_name?message=hello
POST /channel_name <message=hello>
```

Other bits:
-----------
```
GET / (`index.html` for working examples)
GET / (content-type=application/json) = channelConnections
```
