# Player2

A self-contained KaraKara frontend for big screens (showing the
playlist and preview of next track) + singer podiums (showing
lyrics and a "start" button)

## TL;DR

Depending on whether you prefer Docker or Node:
```
docker build -t kk-player2 .
docker run --rm -p 1235:80 -ti kk-player2
```
or
```
npm install
npm run serve
```

And then visit the player at
`http://localhost:1235/#queue_id=my_queue`

## Configuration

Double-click the player to show the options window, where you can set a
custom server / change queue ID / enter Podium mode / etc.

## Dev Setup

If you want to develop new features, by far the easiest way is to run node
on your dev box:

```
npm install
npm run serve
```

Files will automatically get rebuilt and hot-reloaded, no need to even hit
refresh in the browser :)

## Developer Notes

- The big screen is the source of truth for "track ended",
  who will send that message to the server. The podium will
  automatically move to the next track in the list and
  begin the auto-play countdown, but it will not send the
  "track ended" signal itself.
