npx @svgr/cli --icon 1em . --out-dir .
gsed -i 's/import \* as React from "react"/import h from "hyperapp-jsx-pragma"/' *.js
