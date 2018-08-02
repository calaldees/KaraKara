npm install      # install build toolchain
npm run build    # compile src/* to lib/*
npm run watch    # auto-compile on changes


new features since player1:
- nicer code (half the lines, double the features)
- theme which is both nice and legal
  - theme is a karakara setting which can be changed on the fly
- podium mode
  - a button for singers to push to start for themselves
  - lyrics on screen without distracting video
  - performer's name to hopefully avoid the wrong singer
  - auto-play after X seconds between each song
- video mode
  - soft subs - if the singer is using the podium view, subs can be disabled
    for the big screen
  - MTV-style credits overlay at the start of each song
- no more demo mode - opening index.html from the local drive with the file://
  protocol will do a tiny bit of stubbing to force hostname=karakara.org.uk
  and queue_id=shish, and it will talk to the real live server from then on.

NOTES:
- when in auto-play mode, the podium is the source of truth for hitting "play"
  (what do we do if we only have admin + big screen, no podium? Should both
  interfaces have a timer and both send the "play" signal, and we rely on
  deduping? The big screen should be delayed a couple of seconds to give a
  laggy podium a chance to go first)
- the big screen is the source of truth for "track ended", who will send that
  message to the server. The podium will automatically move to the next track
  in the list and begin the auto-play countdown, but it will not send the
  "track ended" signal itself.

TODO:
- ensure that repeated "ended" signals are only handled once
  - also on the server side? Client should specify *which* track has ended,
    so the server can ignore that message if the track in question has already
	gone?
- get the auth token from the HTTP header, because when doing CORS the client
  can't actually see the cookie that it needs to send to the websocket server
- are there any hardsub-only songs, without .srt files? For those, the podium
  should display the video instead of an empty lyric sheet
- lyrics embedded in the queue.json would be wonderful, so that we don't need
  to go and fetch and parse the .srt for ourselves for every song for every
  queue update...
