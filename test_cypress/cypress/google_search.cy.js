describe('Google Search', () => {
	it('Search for live KaraKara webpage', () => {
		cy.visit("https://www.google.com");
		// Bypass cookie warning (EU only) - this fails when run on GitHub's US server
		cy.get('button').contains("Accept all").scrollIntoView().should('be.visible').click();
		// * Perform a google search for project (with a spelling mistake)
		cy.get('input[title="Search"]').should('be.visible').type("KaraKara uk{enter}");
		// * Check that `karakara.uk` is somewhere in the returned list of searches
		cy.contains("karakara.uk").click();
		// * Follow the google search link to the live website
		cy.get('h1').contains('KaraKara').should('be.visible');
	});
});
