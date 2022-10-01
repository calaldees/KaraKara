describe('empty spec', () => {
  it('Correct admin login brings us to remote control', () => {
    cy.visit('https://karakara.uk/browser2/')
    cy.get("h1").dblclick()
    cy.get("input").eq(2).type("demo")
    cy.get("input").eq(3).type("demo")
    cy.contains("Close").click()
    cy.contains("Remote Control")
    cy.contains("Now Playing").should('not.exist')
  })
  it('Incorrect admin login brings us to now playing', () => {
    cy.visit('https://karakara.uk/browser2/')
    cy.get("h1").dblclick()
    cy.get("input").eq(2).type("demo")
    cy.get("input").eq(3).type("fail")
    cy.contains("Close").click()
    cy.contains("Now Playing")
    cy.contains("Remote Control").should('not.exist')
  })
})