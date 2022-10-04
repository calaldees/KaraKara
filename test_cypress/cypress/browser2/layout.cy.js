describe('Portrait vs Landscape', () => {
  beforeEach(function () {
    cy.intercept('GET', '/files/tracks.json', { fixture: 'tracks.json' })
    cy.visit('/browser2/')
    cy.get("input").eq(0).type("test")
    cy.contains("Enter Room").click()
  })
  it('Portrait', () => {
    cy.viewport(600, 1000);
    cy.contains("Explore Tracks").should('exist')
    // queue is a separate screen
    cy.contains("Now Playing").should('not.exist')
    cy.get('[data-cy="queue"]').click()
    cy.contains("Now Playing").should('exist')
  })
  it('Landscape', () => {
    cy.viewport(1000, 600);
    cy.contains("Explore Tracks").should('exist')
    // queue is always showing, no button for it
    cy.contains("Now Playing").should('exist')
    cy.get('[data-cy="queue"]').should('not.exist')
  })
})