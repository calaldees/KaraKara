/// <reference types="Cypress" />

export {};

describe("Room Settings Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "small_tracks.json",
        }).as("tracks");
    });
    it("Should show some settings", () => {
        cy.visit("/demo/settings");
        cy.contains("Room Settings").should("exist");
        // FIXME: make sure there are some settings
    });
    it.skip("Save settings", () => {
        // FIXME: test saving
    });
    it.skip("Reject invalid settings", () => {
        // FIXME: test saving
    });
});
