# Browser2

A self-contained client-side version of the KaraKara library browser

## TL;DR

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

And then visit the browser at
`http://localhost:1234/`

## Dev Setup

If you want to develop new features, by far the easiest way is to run node
on your dev box:

```
npm install
npm run serve
```

Files will automatically get rebuilt and hot-reloaded, no need to even hit
refresh in the browser :)
