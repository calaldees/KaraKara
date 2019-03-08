# Player2

A self-contained KaraKara frontend for big screens (showing the
playlist and preview of next track) + singer podiums (showing
lyrics and a "start" button)

## TL;DR:

```
docker build -t kk-player2 .
docker run --rm -p 1234:1234 -ti kk-player2
```

Visit the player at
`http://localhost:1234/#queue_id=my_queue`

Add `&podium` to the end of the URL to get the singer view.

## New Features Since Player1:

- Nicer code (half the lines, double the features)
- New theme which is both nice and legal
- Theme can be changed on the fly
- Podium mode
  - A button for singers to push to start for themselves
  - Lyrics on screen without distracting video
  - Performer's name to hopefully avoid the wrong singer
  - Auto-play after X seconds between each song
- Video mode
  - Soft subs - if the singer is using the podium view, subs
    can be disabled for the big screen
  - MTV-style credits overlay at the start of each song
- Demo mode
  - Removed - Opening `index.html` from the local drive with
    the `file://` protocol will do a tiny bit of stubbing to
    force `hostname=karakara.org.uk` and `queue_id=demo`,
    and it will talk to the real live server from then on.
- Theme Variations
  - eg `theme_var=lite` can be used to disable animations

## Dev Setup:

If you want to develop new features, you can supply your own source code:

```
docker build -t kk-player2 .
docker run --rm -p 1234:1234 -v $(pwd)/src:/app/src -ti kk-player2
```

Or if you have npm installed and want to use local files rather than docker,

```
npm install
npm run watch
```

Also you can add `&hostname=...` to the URL to specify a
particular karakara server (defaults to `karakara.org.uk` if
you open index.html from the local hard drive)

## Developer Notes:

- The big screen is the source of truth for "track ended",
  who will send that message to the server. The podium will
  automatically move to the next track in the list and
  begin the auto-play countdown, but it will not send the
  "track ended" signal itself.

## High-level TODO List:

- Lyrics embedded in the queue.json would be wonderful, so
  that we don't need to go and fetch and parse the .srt for
  ourselves for every song for every queue update...
