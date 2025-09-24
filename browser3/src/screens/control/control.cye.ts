/// <reference types="cypress" />

export {};

describe("Control Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "small_tracks.json",
        }).as("tracks");
        cy.login();
    });
    it("Should show instructions when empty", () => {
        cy.visit("/test/queue");
        cy.contains("READ ME :)").should("exist");
    });
    it.skip("Should support drag & drop to reorder", () => {
        // FIXME
    });
});
