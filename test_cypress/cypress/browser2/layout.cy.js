describe('Portrait vs Landscape', () => {
  beforeEach(function () {
    cy.intercept('GET', '/files/tracks.json', { fixture: 'tracks.json' })
    cy.visit('/browser2/')
    cy.get("input").eq(0).type("demo")
    cy.contains("Enter Room").click()
  })
  it('Portrait', () => {
    cy.viewport(600, 1000);
    cy.contains("Now Playing").should('not.exist')
    cy.contains("Explore Tracks").should('exist')
  })
  it('Landscape', () => {
    cy.viewport(1000, 600);
    cy.contains("Now Playing").should('exist')
    cy.contains("Explore Tracks").should('exist')
  })
})