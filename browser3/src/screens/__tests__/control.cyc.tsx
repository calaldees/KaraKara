/// <reference types="Cypress" />
/// <reference path="../../../cypress/support/component.ts" />

import { Control } from "../control";
import tracks from "../../../cypress/fixtures/small_tracks.json";
import queue from "../../../cypress/fixtures/small_queue.json";
import settings from "../../../cypress/fixtures/small_settings.json";

describe("no tracks", () => {
    it("no tracks", () => {
        cy.mount(<Control />, {
            client: {},
            server: {},
            room: {
                queue: [],
            },
        });
        cy.contains("READ ME :)").should("exist")
    });
});


describe("now playing", () => {
    it("no time", () => {
        cy.mount(<Control />, {
            client: {},
            server: {
                now: 1000,
            },
            room: {
                queue: [
                    {
                        ...queue[1],
                        start_time: null
                    }
                ],
            },
        });
        cy.get("span.count").should('not.exist')
    });
    it("in the future", () => {
        cy.mount(<Control />, {
            client: {},
            server: {
                now: 1000,
            },
            room: {
                queue: [
                    {
                        ...queue[1],
                        start_time: 1120
                    }
                ],
            },
        });
        cy.get("span.count").contains('In 2 mins').should('exist')
    });
    it("playing now", () => {
        cy.mount(<Control />, {
            client: {},
            server: {
                now: 1000,
            },
            room: {
                queue: [
                    {
                        ...queue[1],
                        start_time: 990,
                        track_duration: 60,
                    }
                ],
            },
        });
        cy.get("span.count").contains('Now').should('exist')
    });
});

function dnd(drag: string, drop: string) {
    const dataTransfer = new DataTransfer();

    cy.get(drag).trigger('dragstart', {
        dataTransfer
    });

    cy.get(drop).trigger('drop', {
        dataTransfer
    });
}
describe("drag & drop", () => {
    beforeEach(function () {
        cy.intercept("PUT", "/room/test/queue.json", { body: {} }).as("move");
    });
    it("drag to top", () => {
        cy.mount(<Control />, {
            client: {},
            server: {},
            room: {},
        });
        dnd('[data-item-id="2"]', '[data-item-id="1"]')
        cy.wait('@move').then(({ request, response }) => {
            expect(response?.statusCode).to.eq(200);
            expect(request.body.source).to.eq("2");
            expect(request.body.target).to.eq("1");
        });
    });
    it("drag to bottom", () => {
        cy.mount(<Control />, {
            client: {},
            server: {},
            room: {},
        });
        dnd('[data-item-id="2"]', '[data-cy="end-marker"]')
        cy.wait('@move').then(({ request, response }) => {
            expect(response?.statusCode).to.eq(200);
            expect(request.body.source).to.eq("2");
            expect(request.body.target).to.eq("-1");
        });
    });
});

describe("misc", () => {
    it("playground", () => {
        cy.mount(<Control />, {
            client: {},
            server: {},
            room: {},
        });
        cy.contains("READ ME :)").should("not.exist")
    });
});
