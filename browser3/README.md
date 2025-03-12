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

```
npm run test
```

## Browser support notes

tl;dr: Safari on iOS 11+ or Chrome on Android 8+

- ios15
    - worked out of the box
- ios14
    - null coalescing not supported
        - vite `build.target` set to `es2015` to transpile this
    - `top/left/right/bottom: 0` is being transpiled to `inset: 0`
        - vite `build.target` set to `['es2015', 'ios11']` to fix this
- ios13
    - `user-select: none` is an invalid value?
        - but after setting target to ios11, text-selection is still fixed despite not affecting this??
    - thumbnail images not showing up
- ios12
    - `globalThis` is missing
        - polyfill added
    - `Request.signal` is missing
        - only used for React-Router `Loader`s, and we only use one null-Loader to trigger saving the scroll position. So on iOS-12, we don't set the null-loader.
- ios11
    - `AbortController` is missing
        - polyfill added
- ios10

    - mostly works, except for clicking on categories, which is pretty major o_O

- android 8
    - worked out of the box (after all the stuff for iOS-11 was put in place, so perhaps polyfills are needed but we already have them?)
