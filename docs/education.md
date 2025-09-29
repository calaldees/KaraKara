Education: System Investigation
-------------------------------

These questions are designed for a group exercise in dissecting this codebase as part of a wider education exercise.

* docker (see `compose.yml`)
    * How many containers are needed to run the system?
        * what do they each do?
            * What is mqtt? why is it an important design pattern
* look at `nginx/nginx.conf`
    * What is nginx?
    * what is the purpose of this container?
* Server API (`/api_queue`)
    * What framework is used for the server-state/restAPI?
        * What are some of benefits/features of this framework?
    * Find where some middleware is created - what is this middleware doing?
    * `/docs/` shows an openapi spec - this is generated directly from the code
        * give a permalink to a line number that contributes any information to the openapi spec
        * What language feature has been used to register these extra details with the openapi spec?
        * the framework does not provide this `/docs/` automatically, it's a plugin. Find the url to documentation for this extension/plugin/feature
* Clients (`/player3` and `/browser3`)
    * what framework is used in the clients?
    * what language is used in the clients?
    * look at `index.html` as a file - now look at the source of one of the clients in a browser (with ctrl+u). Which of the packages below is transforming this?
    * looking in `package.json`
        * what is `vite` and why is it used?
        * what is `prettier` and why is it used?
        * what is `@shish2k/react-mqtt` and why is it used?
            * https://www.npmjs.com/package/@shish2k/react-mqtt
    * `npm install`
        * `npm run serve`
            * Load the site - look at the network requests - see the number of ts files - why is this interesting?
        * What testing framework is used in browser3
            * `npm run test`
            * Find out about this test framework - how is it different to jest?
    * what is `player3/src/player.d.ts` - why is this file important?
    * permalink to a line that defines a clients state object
    * Look at `Dockerfile`
        * See the pattern of building, copying and serving with nginx. How big is the image that is created?
* Look at contributions over time https://github.com/calaldees/KaraKara/graphs/contributors
    * Who is the biggest contributor?
    * Look at https://github.com/calaldees/KaraKara/blame/master/browser3/package-lock.json
        * Look how many lies this file is?
        * Question: are these "lines of code?"
        * Should these lines be counted as contributions? why? why not?
* https://github.com/calaldees/KaraKara/commit/e6b91a17e4f292f3851c7aac9d2a10e8a13b4e3d
    * What is happening in this commit? is this good or bad? why?
* With Code IDE
    * looking in `/media`
        * how many source files are needed for each track? what is in the source files?
        * Why are the processed files named they way they are?
        * what is `.vtt`?
        * what is `.webm`?
    * using  `cloc --vcs=git xxx` (where `xxx` could be `processmedia3`/`browser3`/`player3`/`api_queue`)
        * (install with `sudo apt-get update && sudo apt-get install -y cloc`)
        * which is the biggest component in lines of code? (ignoring datafiles)
        * compare `cloc --vcs=git api_queue/api_queue/` and `cloc --vcs=git api_queue/tests/` what is the app-to-test ratio? is this good?
* with `karakara.uk`
    * with browser3 - look at network transfer of `tracks.json` - how big is the file? how much data was transferred? Why is there a difference?
    * What format are the image files in?
        * Why is this interesting? find out more about the format
* with your gitpod/local server or `karakara.uk`
    * Add a track to the playlist using a curl statement (look in the documentation for api_queue)
        * List duration:track_id `curl https://karakara.uk/files/tracks.json | jq '.[] | { d:.duration|tostring, i:.id } | [.d, .i] | join(": ")' | sed 's/"//' | sort -nr`
    * Play and then stop a video using a `curl` statement
    * use `curl` to get the queue as a `csv`. What is csv?
* karakara does not use a database - but still stores data
    * What data storage does the system use?
        * for tracks?
        * for queue/room?
    * Where on the file system is the data stored?
        * permalink to the line that persists/writes some data/state
    * Would using a database be better? why? why not?
* Integration Tests?
    * There are _some_ cypress tests. What site do they test? Is this good/bad? What are your recommendations for what should be tested in future?
* Overall
    * Is karakara multiple programs? or one program? why?
