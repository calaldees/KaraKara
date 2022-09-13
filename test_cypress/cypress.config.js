const { defineConfig } = require('cypress')
module.exports = defineConfig({
    e2e: {
        supportFile: false,
        specPattern: 'cypress/**/*.cy.js',
        videoUploadOnPasses: false,
        screenshotsFolder: 'reports/screenshots',
        videosFolder: 'reports/videos',
        chromeWebSecurity: false,
        reporter: 'junit',
        reporterOptions: {
            mochaFile: 'reports/junit-[hash].xml'
        },
    }
})