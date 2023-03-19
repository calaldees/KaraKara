npx @svgr/cli --icon 1em . --out-dir . --typescript
sed -i '' 's/import \* as React from "react"/import h from "hyperapp-jsx-pragma"/' *.tsx
sed -i '' 's/import { SVGProps } from "react";//' *.tsx
# rename 's/js/tsx/' *.js
