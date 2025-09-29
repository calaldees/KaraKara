# Browser3

A self-contained client-side version of the KaraKara library browser

## Admin Tips

Double-click the title of any screen to get to the app settings screen.

Enter a room password to enter admin mode with extra buttons visible.

## Layout

```
src/
  components/  -- commonly used widgets
  hooks/       -- custom react hooks
  providers/   -- global state providers (track list, client settings, etc)
  screens/     -- each screen of the app
  static/      -- static files (eg. CSS that isn't associated with any specific screen)
  utils/       -- common utility functions
  browser.tsx  -- main app, initialises routing, global providers, first screen
  types.ts     -- type definitions, should be in-sync with player3 and api_queue
```
Source code in `src/`, compiled results in `dist/`

Each screen has its own specific state and rendering functions in `src/screens/`

Global state (eg track list, queue, server time) is set in `src/providers/`

## Architecture

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
     \- QR Code (admin only)

```

## Dev Setup

Depending on whether you prefer Docker or Node:

```
docker build -t kk-browser3 .
docker run --rm -p 1236:80 -ti kk-browser3
```

or

```
npm install
npm run serve
```

And then visit the browser at `http://localhost:1236/`

With `npm run serve`, files will automatically get rebuilt and
hot-reloaded, no need to even hit refresh in the browser :)

Unit tests for the more processing-heavy parts of the code can
be run with:

## Testing

Unit tests for the more processing-heavy parts of the code
(basically just the parts in `src/utils`)
```
npm run test
```

Automated end-to-end tests using Cypress
```
```
