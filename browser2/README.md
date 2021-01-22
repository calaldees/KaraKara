# Browser2

A self-contained client-side version of the KaraKara library browser

## Admin Tips

Double-click the title of any screen to get to the app settings screen.

Enter a room password to enter admin mode with extra buttons visible.

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
