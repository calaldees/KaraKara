/// <reference types="Cypress" />

export {};

describe("Printable Screen", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", {
            fixture: "small_tracks.json",
        }).as("tracks");
    });
    it("mention the room name", () => {
        cy.visit("/testroom/printable");
        cy.contains('room name "testroom"').should("exist");
    });
    it.skip("show a QR code", () => {
        cy.visit("/testroom/printable");
        // FIXME: test that the QR code exists - and is valid?
    });
});
