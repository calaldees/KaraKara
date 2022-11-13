Getting Started with KaraKara
=============================

unfinished...

karakara.uk Tour
-----------

* https://karakara.uk/
    Room: test
* https://karakara.uk/player2/
* double click title banner
    * username: test, password: test
* Developers
    * https://karakara.uk/docs
    * https://karakara.uk/community2/queue_view.html#test


Run it locally or the cloud
--------------

### Checkout

#### GitPod (Cloud)
https://gitpod.io#https://github.com/calaldees/KaraKara

#### Local
```bash
git clone https://github.com/calaldees/KaraKara.git
cd KaraKara
```

### Run
```bash
python3 media/get_example_media.py
docker-compose up --build

# see encoding progress
docker-compose exec processmedia2 /bin/bash
    python3 metaviewer.py
    top
    # KAT-TUN took 8min, Captain America took 25min (cpu is throttled after light use)

# api_queue -> track_id invalid
# when encoding complete - api_queue must be restarted to load new `tracks.json`
docker-compose restart api_queue
```


Education: System Investigation
-------------------------------

These questions are designed for a group exercise in dissecting this codebase as part of a wider education exercise.

* docker (see `docker-compose.yml`)
    * How many containers are needed to run the system?
        * what do they each do?
            * What is mqtt? why is it an important design pattern
* look at `nginx/ngonx.conf`
    * What is nginx?
    * what is the purpose of this container?
* karakara does not use a database - but still stores data
    * what data storage does the system use?
        * for tracks?
        * for queue/room?
    * where on the file system is the data stored?
        * permalink to the line that persists the queue data
    * would using a database be better? why? why not?
* Server API (api_queue)
    * What framework is used for the server-state/restAPI?
        * What are some of benefits/features of this framework?
    * Find where some middleware is created - what is this middleware doing?
    * `/docs/` shows an openapi spec - this is generated directly from the code
        * give a permalink to a line number that contributes any information to the openapi spec
        * What language feature has been used to register these extra details with the openapi spec?
        * the framework does not provide this `/docs/` automatically, it's a plugin. Find the url to documentation for this extension/plugin/feature
* Clients (player2 and browser2)
    * what framework is used in the clients?
    * what language is used in the clients?
    * looking in `package.json`
        * what is `prettier` and why is it used?
        * what is `parcel` and why is it used?
        * what is `hyperapp-jsx-pragma` and why is it used?
    * What testing framework is used in browser2
    * what is `player.d.ts` - why is this file important?
    * permalink to a line that defines a clients state object
* Look at contributions over time https://github.com/calaldees/KaraKara/graphs/contributors
    * https://github.com/calaldees/KaraKara/blame/master/browser2/package-lock.json
    * Question: are these "lines of code?"
    * Should these lines be counted as contributions? why? why not?
* https://github.com/calaldees/KaraKara/commit/e6b91a17e4f292f3851c7aac9d2a10e8a13b4e3d
    * What is happening in this commit? is this good or bad? why?
* With gitpod/local
    * looking in `media` 
        * how many source files are needed for each track? what is in the source files?
        * ```bash
            # in new terminal while containers are running
            docker-compose exec processmedia2 /bin/bash
            python3 metaviewer.py
            ```
        * Why are the processed files named they way they are?
        * what is `vtt`? what is `webm`?
    * using  `cloc --vcs=git xxx` `processmedia2/browser2/player2/api_queue`
        * which is the biggest component in lines of code?
        * compare `cloc --vcs=git api_queue/api_queue/` and `cloc --vcs=git api_queue/tests/` what is the app-to-test ratio? is this good?
* with `karakara.uk`
    * with browser2 - look at network transfer of `tracks.json` - how big is the file? how much data was transferred? Why is there a difference?
    * What format are the image files in?
        * Why is this interesting? find out more about the format
* with your gitpod/local server or `karakara.uk`
    * Add a track to the playlist using a curl statement (look in the documentation for api_queue)
        * `curl https://karakara.uk/files/tracks.json | jq '.[] | { d:.duration|tostring, i:.id } | [.d, .i] | join(": ")' | sed 's/"//' | sort -nr`
    * Play and then stop a video using a curl statement
    * use curl to get the queue as a `csv`. What is csv?
* Integration Tests?
    * There are _some_ cypress tests. What site do they test? Is this good/bad? What are your recommendations for what should be tested in future?
* Overall
    * Is karakara multiple programs? or one program? why?
