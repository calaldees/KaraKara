/// <reference types="cypress" />
/// <reference path="../../../cypress/support/commands.ts" />

export {};

describe("Room Settings Screen", () => {
    beforeEach(() => {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "small_tracks.json",
        }).as("tracks");
    });
    it("Should show some settings", () => {
        cy.login();
        cy.contains("Room Settings").click();
        cy.contains("Room Settings").should("exist");
        cy.get("#root_title").should("exist");
    });
    it("Save settings", () => {
        cy.login();
        cy.contains("Room Settings").click();
        cy.contains("Room Settings").should("exist");
        cy.get("#root_title").should("exist");
        cy.get("#root_title").clear().type("test title");
        cy.get("[data-cy=save-settings-button]").click();
        cy.contains("Settings saved").should("exist");
    });
    it("Reject invalid settings", () => {
        cy.login();
        cy.contains("Room Settings").click();
        cy.contains("Room Settings").should("exist");
        cy.get("#root_coming_soon_track_count").should("exist");
        cy.get("#root_coming_soon_track_count").clear().type("99");
        cy.get("[data-cy=save-settings-button]").click();
        // RJSF should show validation error for max value of 9
        cy.get(".field-error").should("exist");
    });
});
