/// <reference types="cypress" />

export {};

describe("Portrait vs Landscape", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", '"1234"');
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "small_tracks.json",
        });
    });
    it("Portrait", () => {
        cy.viewport(600, 1000);
        cy.visit("/test");
        cy.contains("Explore Tracks").should("exist");
        // queue is a separate screen
        cy.contains("Now Playing").should("not.exist");
        cy.get('[data-cy="queue"]').click();
        cy.contains("Now Playing").should("exist");
    });
    it("Landscape", () => {
        cy.viewport(1000, 600);
        cy.visit("/test");
        cy.contains("Explore Tracks").should("exist");
        // queue is always showing, no button for it
        cy.contains("Now Playing").should("exist");
        cy.get('[data-cy="queue"]').should("not.exist");
    });
    it("Portrait-to-Landscape", () => {
        cy.viewport(600, 1000);
        cy.visit("/test");
        cy.contains("Explore Tracks").should("exist");
        cy.contains("Now Playing").should("not.exist");
        cy.viewport(1000, 600);
        cy.contains("Explore Tracks").should("exist");
        cy.contains("Now Playing").should("exist");
    });
    it("Landscape-to-Portrait", () => {
        cy.viewport(1000, 600);
        cy.visit("/test");
        cy.contains("Explore Tracks").should("exist");
        cy.contains("Now Playing").should("exist");
        cy.viewport(600, 1000);
        cy.contains("Explore Tracks").should("exist");
        cy.contains("Now Playing").should("not.exist");
    });
});
