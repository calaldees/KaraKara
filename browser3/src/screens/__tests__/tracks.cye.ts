/// <reference types="Cypress" />

export {};

describe("Filters", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", { fixture: "tracks.json" });
        cy.visit("/test");
    });
    it("Small categories directly list tracks", () => {
        cy.contains("child").click();
        cy.contains("Roger Ramjet").click();
        cy.contains("Lyrics").should("exist");
    });
    it("Large categories are grouped by letter", () => {
        cy.contains("anime").click();
        cy.contains("AKB0048").should("not.exist");
        cy.contains("A").click();
        cy.contains("AKB0048").click();
        cy.contains("Kibou ni Tsuite").click();
        cy.contains("Lyrics").should("exist");
    });
    it("Large tags with subtags have groups", () => {
        cy.contains("anime").click();
        cy.contains("M").click();
        cy.contains("Macross").click();
        cy.contains("Macross 7").click();
        cy.contains("Planet Dance").click();
        cy.contains("Lyrics").should("exist");
    });
    it("Back button removes one level at a time", () => {
        cy.contains("anime").click();
        cy.location("search").should("eq", "?search=&filters=category%3Aanime");
        cy.contains("M").click();
        cy.contains("Macross").click();
        cy.location("search").should(
            "eq",
            "?search=&filters=category%3Aanime&filters=from%3AMacross",
        );
        cy.contains("Macross 7").click();
        cy.location("search").should(
            "eq",
            "?search=&filters=category%3Aanime&filters=from%3AMacross&filters=Macross%3AMacross+7",
        );
        cy.contains("Planet Dance").click();
        cy.location("search").should("eq", "");
        cy.contains("Lyrics").should("exist");

        cy.get('[data-cy="back"]').click();
        cy.location("search").should(
            "eq",
            "?search=&filters=category%3Aanime&filters=from%3AMacross&filters=Macross%3AMacross+7",
        );
        cy.get('[data-cy="back"]').click();
        cy.location("search").should(
            "eq",
            "?search=&filters=category%3Aanime&filters=from%3AMacross",
        );
        cy.get('[data-cy="back"]').click();
        cy.location("search").should("eq", "?search=&filters=category%3Aanime");
        cy.get('[data-cy="back"]').click();
        cy.location("search").should("eq", "?search=");
        cy.get('[data-cy="back"]').should("not.exist");
    });
});
describe("Search", () => {
    beforeEach(function () {
        cy.intercept("GET", "/time.json", { body: 1234 });
        cy.intercept("GET", "/files/tracks.json", { fixture: "tracks.json" });
        cy.visit("/test");
    });
    it("should pick tracks", () => {
        cy.get('[data-cy="search"]').type("Tashikametai");
        cy.contains("My Heart").click();
    });
    it("browser back button removes search as a single unit", () => {
        cy.contains("anime").click();
        cy.location("search").should("eq", "?search=&filters=category%3Aanime");
        cy.get('[data-cy="search"]').type("magic");
        cy.location("search").should(
            "eq",
            "?search=magic&filters=category%3Aanime",
        );
        cy.contains("Gundam").click();
        cy.location("search").should(
            "eq",
            "?search=magic&filters=category%3Aanime&filters=from%3AGundam",
        );

        cy.go("back");
        cy.location("search").should(
            "eq",
            "?search=magic&filters=category%3Aanime",
        );
        cy.go("back");
        cy.location("search").should("eq", "?search=&filters=category%3Aanime");
        cy.go("back");
        cy.location("search").should("eq", "?search=");
    });
});
