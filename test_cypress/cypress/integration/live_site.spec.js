describe('Google Search', () => {
	it('Search for live KaraKara webpage', () => {
		cy.visit("https://www.google.com");
		// * Perform a google search for project (with a spelling mistake)
		cy.contains("I agree").scrollIntoView().should('be.visible').click();
		cy.get('input[title="Search"]').should('be.visible').type("KaraKara uk{enter}");
		// * Check that `karakara.uk` is somewhere in the returned list of searches
		cy.contains("karakara.uk").click();
		// * Follow the google search link to the live website
		cy.get('h1').contains('KaraKara').should('be.visible');
	});
});
