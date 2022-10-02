describe('Bookmarks', () => {
  beforeEach(function () {
    cy.intercept('GET', '/files/tracks.json', { fixture: 'tracks.json' })
    cy.visit('/browser2/')
    cy.get("input").eq(0).type("demo")
    cy.contains("Enter Room").click()
  })
  it('Add, check, remove, check', () => {
    // Add
    cy.contains("jdrama").click()
    cy.contains("Birth").click()
    cy.contains("Bookmark").click()
    // Check that it was added
    cy.get('[data-cy="back"]').click()
    cy.get('[data-cy="back"]').click()
    cy.contains("Bookmarks")
    cy.contains("Birth").click()
    // Remove
    cy.contains("Un-Bookmark").click()
    cy.get('[data-cy="back"]').click()
    // Check that it was removed
    cy.contains("Bookmarks").should('not.exist')
    cy.contains("Birth").should('not.exist')
  })
})