# Player2

A self-contained KaraKara frontend for big screens (showing the
playlist and preview of next track) + singer podiums (showing
lyrics and a "start" button)

## Admin Tips

Double-click the player to show the options window, where you can
set a custom server / change queue ID / enter Podium mode / etc.

## Architecture

Source code in `src/`, compiled results in `dist/`

All of the app state is specified in `src/player.d.ts` (initialised in
`src/player.tsx`)

State is turned into HTML via the templates in `src/screens/`

State is mostly updated by `src/subs.tsx` - In this case we mostly listen
on the MQTT channel `/karakara/rooms/<roomname>/commands` - commands are
things like "play", "pause", "skip", etc which directly update the state;
but also "update_queue" which will trigger an HTTP fetch for
`queue_items.json` (placing the response into `state.queue_items`) and
"settings" which will trigger an HTTP fetch for `settings.json` (placing
the response into `state.settings`).

In the future we could replace "broadcast a command, which triggers JSON
fetch over HTTP" with "broadcast JSON"

## Dev Setup

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

And then visit the player at `http://localhost:1235/`

With `npm run serve`, files will automatically get rebuilt and
hot-reloaded, no need to even hit refresh in the browser :)

If you want to see the whole state for the app, you can double-click
anywhere on the screen to open the settings menu, and then click the
"Settings" heading to write the state to the debug console.

## Developer Notes

- The big screen is the source of truth for "track ended",
  who will send that message to the server. The podium will
  automatically move to the next track in the list and
  begin the auto-play countdown, but it will not send the
  "track ended" signal itself.
