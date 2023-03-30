# Browser3

A self-contained client-side version of the KaraKara library browser

## Admin Tips

Double-click the title of any screen to get to the app settings screen.

Enter a room password to enter admin mode with extra buttons visible.

## Architecture

Source code in `src/`, compiled results in `dist/`

Each screen has its own specific state and rendering functions in `src/screens/`

Global state (eg track list, queue, server time) is set in `src/providers/`

## Layout

Click things to go towards the leaves, click the "Back" button to go towards
the root.

```
Login
 \- Explore
     |- Explore (with more filters)
     |   \- [...]
     |- Track Details
     |   \- Queue (if user) / Control (if admin)
     |- Queue (if user) / Control (if admin)
     |- Settings (admin only)
     \- Tracklist (admin only)

```

## Dev Setup

Depending on whether you prefer Docker or Node:
```
docker build -t kk-browser3 .
docker run --rm -p 1234:80 -ti kk-browser3
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

Unit tests for the more processing-heavy parts of the code can
be run with:

```
npm run test
```