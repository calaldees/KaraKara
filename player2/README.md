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

State is turned into HTML via the templates in `src/screens/`. `root.tsx`
contains the logic which decides which screen we're on (title, preview,
video, etc)

State is mostly updated by `src/subs.tsx` - we have an MQTT subscription
which listens to topics under `/room/<roomname>/...`:

- `queue` - JSON, each update goes to `state.queue`
- `settings` - JSON, each update goes to `state.settings`

(There are also some keyboard shortcuts to trigger play / pause / etc
locally, for easier development)

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
