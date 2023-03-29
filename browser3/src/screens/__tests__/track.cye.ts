/// <reference types="Cypress" />

export {};

describe("Bookmarks", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", { fixture: "tracks.json" });
        cy.visit("/test");
    });
    it("Add, check, remove, check", () => {
        // Add
        cy.contains("child").click();
        cy.contains("Ramjet").click();
        cy.contains("Bookmark").click();
        // Check that it was added
        cy.get('[data-cy="back"]').click();
        cy.get('[data-cy="back"]').click();
        cy.contains("Bookmarks");
        cy.contains("Ramjet").click();
        // Remove
        cy.contains("Un-Bookmark").click();
        cy.get('[data-cy="back"]').click();
        // Check that it was removed
        cy.contains("Bookmarks").should("not.exist");
        cy.contains("Ramjet").should("not.exist");
    });
});
describe("Metadata", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", { fixture: "tracks.json" });
        cy.visit("/test");
    });
    it("Tags", () => {
        cy.contains("child").click();
        cy.contains("Ramjet").click();
        cy.contains("Tags").should("exist");
    });
});
