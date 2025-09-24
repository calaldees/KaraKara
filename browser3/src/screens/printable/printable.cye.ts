/// <reference types="cypress" />

export {};

describe("Printable Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "small_tracks.json",
        }).as("tracks");
    });
    it("mention the room name", () => {
        cy.login();
        cy.contains("Printable QR Code").click();
        cy.contains('room name "test"').should("exist");
    });
    it("show a QR code", () => {
        cy.login();
        cy.contains("Printable QR Code").click();
        cy.get("svg").should("exist");
    });
});
