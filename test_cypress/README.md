
I have my own old notes about cypress
https://github.com/calaldees/cypress-for-ci

https://docs.cypress.io/examples/examples/docker#Images

https://github.com/bahmutov/cypress-open-from-docker-compose
* [Run Cypress with a single Docker command](https://www.cypress.io/blog/2019/05/02/run-cypress-with-a-single-docker-command/)

The official images seem to have the same reports problem from 3 years ago - maybe some of my old hacks will help

why is cypress/included:8.3.0 3GB!?

```cmd
    # Windows ADMIN console
    choco install nodejs

    # in test_cypress dir
    npm install cypress

    set CYPRESS_BASE_URL=http://localhost/
    npx cypress open
```


* Run with
    * Local Headless: `npx cypress run --spec cypress/integration/google.spec.js`
    * Container Headless: `make cypress_cmd CYPRESS_CMD="run --spec cypress/integration/example.spec.js"`