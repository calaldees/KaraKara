/// <reference types="Cypress" />

export {};

describe("Loading Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "tracks.json",
            throttleKbps: 500,
        }).as("tracks");
    });
    it("Login page should display directly until user tries to log in", () => {
        cy.visit("/");
        cy.contains("Enter Room").should("exist");
        cy.contains("Loading...").should("not.exist");

        cy.get("input").eq(0).type("test");
        cy.contains("Enter Room").click();
        cy.contains("Loading...").should("exist");
        cy.contains("Explore Tracks").should("not.exist");

        cy.wait("@tracks");
        cy.contains("Loading...").should("not.exist");
        cy.contains("Explore Tracks").should("exist");
    });
    it("Room should show loading screen and then room", () => {
        cy.visit("/demo");
        cy.contains("Loading...").should("exist");
        cy.contains("Explore Tracks").should("not.exist");

        cy.wait("@tracks");
        cy.contains("Loading...").should("not.exist");
        cy.contains("Explore Tracks").should("exist");
    });
});
