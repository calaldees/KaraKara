import inputArray from "rollup-plugin-input-array";
import postcss from 'rollup-plugin-postcss'
import jsx from 'rollup-plugin-jsx';
import babel from 'rollup-plugin-babel';
import resolve from 'rollup-plugin-node-resolve';
// import commonjs from 'rollup-plugin-commonjs';
import { uglify } from 'rollup-plugin-uglify';

import glob from 'glob';
let styles = glob.sync("src/**/*.scss").map(a => "./" + a);

// `npm run build` -> `production` is true
// `npm run dev` -> `production` is false
const production = !process.env.ROLLUP_WATCH;


export default {
    input: ['./src/player.js'].concat(styles),
    output: {
        file: 'lib/player.js',
        format: 'iife',
        sourcemap: true,
        name: 'playerMod',
    },
    plugins: [
        inputArray(),
        postcss({
            extract: true,
            plugins: [
                require('cssnano')({
                    preset: 'default',
                })
            ]
        }),
        jsx({
            factory: 'h'
        }),
        babel({
            exclude: 'node_modules/**'
        }),
        resolve(),
        //commonjs(),
        production && uglify(), // minify, but only in production
    ]
};