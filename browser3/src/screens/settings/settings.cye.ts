/// <reference types="cypress" />

export {};

describe("Room Settings Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "small_tracks.json",
        }).as("tracks");
    });
    it("Should show some settings", () => {
        cy.login();
        cy.contains("Room Settings").click();
        cy.contains("Room Settings").should("exist");
        cy.contains("title:").should("exist");
    });
    it.skip("Save settings", () => {
        cy.login();
        cy.contains("Room Settings").click();
        cy.contains("Room Settings").should("exist");
        cy.contains("title:").should("exist");
        cy.get("[name=title]").should("exist");
        cy.get("[name=title]").clear().type("test title");
        cy.get("[data-cy=save-settings-button]").click();
        cy.contains("Settings saved").should("exist");
    });
    it.skip("Reject invalid settings", () => {
        // FIXME: test saving
    });
});
