/// <reference types="Cypress" />

export {};

describe("Queue Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "tracks.json",
        }).as("tracks");
    });
    it("Should show empty when empty", () => {
        cy.visit("/test/queue");
        cy.contains("Queue Empty").should("exist");
    });
    it("Should reflect added track, and allow removal", () => {
        cy.visit("/test");
        cy.contains("anime").click();
        cy.contains("A").click();
        cy.contains("Air").click();
        cy.contains("Tori").click();
        cy.contains("Enqueue").click();
        cy.get('input[name="performer_name"]').type("Test User");
        cy.contains("Confirm").click();
        cy.contains("is up now!").should("exist");
        cy.get("[data-cy='remove']").click();
        cy.contains("is up now!").should("not.exist");
    });
});
