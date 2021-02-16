# Browser2

A self-contained client-side version of the KaraKara library browser

## Admin Tips

Double-click the title of any screen to get to the app settings screen.

Enter a room password to enter admin mode with extra buttons visible.

## Architecture

Source code in `src/`, compiled results in `dist/`

All of the app state is specified in `src/browser.d.ts` (initialised in
`src/browser.tsx`)

State is turned into HTML via the templates in `src/screens/`

State is updated in two ways:

- Actions - functions which take a `State` as input and return a
  modified `State` as output, normally linked to an onclick handler.
  - Eg `<li onclick={(state) => ({...state, track_id: 'abcd'})}>MyTrack</li>` -
    "When I click this track name, update state so that it's the same
    as it was except for state.track_id being abcd"
- An MQTT subscription (in `src/subs.tsx`) to topics under
  `/karakara/room/<roomname>/...`:
  - `queue` - JSON, each update goes to `state.queue`
  - `settings` - JSON, each update goes to `state.settings`
  - `notifications` - Text, each message is turned into a notification

## Dev Setup

Depending on whether you prefer Docker or Node:
```
docker build -t kk-browser2 .
docker run --rm -p 1234:80 -ti kk-browser2
```
or
```
npm install
npm run serve
```

And then visit the browser at `http://localhost:1234/`

With `npm run serve`, files will automatically get rebuilt and
hot-reloaded, no need to even hit refresh in the browser :)

After double-clicking any title to get to the app settings, click on
"Settings" to write out the current state to the debug console.
