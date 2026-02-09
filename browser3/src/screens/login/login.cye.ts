/// <reference types="cypress" />

export {};

describe("Login Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json?ver=*", {
            fixture: "small_tracks.json",
        }).as("tracks");
    });
    it("Login should be disabled with no room name", () => {
        cy.visit("/");
        cy.contains("Enter Room").should("be.disabled");
    });
    it("Login page should go to /roomname", () => {
        cy.visit("/");
        cy.contains("Enter Room").should("exist");
        cy.contains("Loading...").should("not.exist");

        cy.get("input").eq(0).type("test");
        cy.contains("Enter Room").click();

        cy.wait("@tracks");
        cy.contains("Loading...").should("not.exist");
        cy.contains("Explore Tracks").should("exist");

        cy.url().should("include", "/test");
    });
});
