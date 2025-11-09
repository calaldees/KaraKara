# Browser3

A self-contained client-side version of the KaraKara library browser

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
dist/          -- compiled results for serving to users
```

## Architecture

Click things to go towards the leaves, click the "Back" button to go towards the root.

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
docker build -t kk-browser3 --build-context root=.. .
docker run --rm -p 1236:80 -ti kk-browser3
```

or

```
npm install
npm run serve
```

And then visit the browser at `http://localhost:1236/`

With `npm run serve`, files will automatically get rebuilt and hot-reloaded, no need to even hit refresh in the browser :)

## Testing

Unit tests for the more processing-heavy parts of the code (basically just the parts in `src/utils`)

```
npm run test
```

Automated end-to-end GUI tests using Cypress

```
npm run cypress
```
