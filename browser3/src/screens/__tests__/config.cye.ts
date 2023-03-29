/// <reference types="Cypress" />

export {};

describe("Admin Login", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", { fixture: "small_tracks.json" });
        cy.visit("/");
        cy.get("h1").dblclick();
        cy.viewport(1000, 600);
    });
    it("Correct admin login brings us to remote control", () => {
        cy.intercept("GET", "/room/test/login.json", {
            body: { is_admin: true },
        });
        cy.get("input").eq(2).type("test");
        cy.get("input").eq(3).type("test");
        cy.contains("Close").click();
        cy.contains("Remote Control").should("exist");
        cy.contains("Room Settings").should("exist");
        cy.contains("Now Playing").should("not.exist");
    });
    it("Incorrect admin login brings us to now playing", () => {
        cy.intercept("GET", "/room/test/login.json", {
            body: { is_admin: false },
        });
        cy.get("input").eq(2).type("test");
        cy.get("input").eq(3).type("fail");
        cy.contains("Close").click();
        cy.contains("Now Playing").should("exist");
        cy.contains("Remote Control").should("not.exist");
    });
    it("Admin login in booth mode doesn't show room settings", () => {
        cy.intercept("GET", "/room/test/login.json", {
            body: { is_admin: true },
        });
        cy.get("input").eq(2).type("test");
        cy.get("input").eq(3).type("test");
        cy.get("input").eq(4).check();
        cy.contains("Close").click();
        cy.contains("Remote Control").should("exist");
        cy.contains("Room Settings").should("not.exist");
        cy.contains("Now Playing").should("not.exist");
    });
});
