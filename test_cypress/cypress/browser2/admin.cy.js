describe('Admin Login', () => {
  beforeEach(function () {
    cy.intercept('GET', '/files/tracks.json', { fixture: 'tracks.json' })
    cy.visit('/browser2/')
    cy.get("h1").dblclick()
  })
  it('Correct admin login brings us to remote control', () => {
    cy.get("input").eq(2).type("test")
    cy.get("input").eq(3).type("test")
    cy.contains("Close").click()
    cy.contains("Remote Control")
    cy.contains("Now Playing").should('not.exist')
  })
  it('Incorrect admin login brings us to now playing', () => {
    cy.get("input").eq(2).type("test")
    cy.get("input").eq(3).type("fail")
    cy.contains("Close").click()
    cy.contains("Now Playing")
    cy.contains("Remote Control").should('not.exist')
  })
})