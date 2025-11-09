# Player3

A self-contained KaraKara frontend for big screens (showing the
playlist and preview of next track) + singer podiums (showing
lyrics and a "start" button)

## Admin Tips

Double-click the player to show the options window, where you can
set a custom server / change queue ID / enter Podium mode / etc.

## Architecture

Source code in `src/`, compiled results in `dist/`

Each screen has its own specific state and rendering functions in `src/screens/`

Global state (eg track list, queue, server time) is set in `src/providers/`

## Dev Setup

Depending on whether you prefer Docker or Node:

```
docker build -t kk-player3 --build-context root=.. .
docker run --rm -p 1237:80 -ti kk-player3
```

or

```
npm install
npm run serve
```

(With `npm run serve`, files will automatically get rebuilt and
hot-reloaded, no need to even hit refresh in the browser :) )

With the player running, visit it at `http://localhost:1237/`

Since player3 is designed to run specifically on projector screens,
it can be useful to use the "Responsive Design Mode" developer tools
and set the display size to either 480x360 (4:3) or 640:360 (16:9) to
ensure that the layout works on either ratio.

Everything in player3's design is measured in `vh` and `vw` CSS units,
where `vh` = 1% of visible displayport height and `vw` is the same for
width.
