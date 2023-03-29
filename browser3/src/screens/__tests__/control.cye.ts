/// <reference types="Cypress" />

export {};

describe("Control Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "small_tracks.json",
        }).as("tracks");
        cy.visit("/");
        cy.get("h1").dblclick();
        cy.get("input").eq(2).type("test");
        cy.get("input").eq(3).type("test");
        cy.contains("Close").click();
    });
    it("Should show instructions when empty", () => {
        cy.visit("/test/queue");
        cy.contains("READ ME :)").should("exist");
    });
    it.skip("Should support drag & drop to reorder", () => {
        // FIXME
    });
});
