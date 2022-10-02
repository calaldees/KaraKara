describe('Search', () => {
  beforeEach(function () {
    cy.intercept('GET', '/files/tracks.json', { fixture: 'tracks.json' })
    cy.visit('/browser2/')
    cy.get("input").eq(0).type("demo")
    cy.contains("Enter Room").click()
  })
  it('Small categories directly list tracks', () => {
    cy.contains("jdrama").click()
    cy.contains("Love So Sweet").click()
    cy.contains("Lyrics")
  })
  it('Large categories are grouped by letter', () => {
    cy.contains("anime").click()
    cy.contains("AKB0048").should('not.exist')
    cy.contains("A").click()
    cy.contains("AKB0048").click()
    cy.contains("Kibou ni Tsuite").click()
    cy.contains("Lyrics")
  })
  it('Large tags with subtags have groups', () => {
    cy.contains("anime").click()
    cy.contains("M").click()
    cy.contains("Macross").click()
    cy.contains("Macross 7").click()
    cy.contains("Planet Dance").click()
    cy.contains("Lyrics")
  })
})