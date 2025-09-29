/// <reference types="cypress" />
/// <reference path="../../../cypress/support/component.ts" />

import { Control } from "./control";
//import tracks from "@/../cypress/fixtures/small_tracks.json";
import queue from "@/../cypress/fixtures/small_queue.json";
//import settings from "@/../cypress/fixtures/small_settings.json";

describe("no tracks", () => {
    it("no tracks", () => {
        cy.mount(<Control />, {
            room: {
                queue: [],
            },
        });
        cy.contains("READ ME :)").should("exist");
    });
});

describe("now playing", () => {
    it("no time", () => {
        cy.mount(<Control />, {
            serverTime: { now: 1000 },
            room: {
                queue: [
                    {
                        ...queue[1],
                        start_time: null,
                    },
                ],
            },
        });
        cy.get("span.count").should("not.exist");
    });
    it("in the future", () => {
        cy.mount(<Control />, {
            serverTime: { now: 1000 },
            room: {
                queue: [
                    {
                        ...queue[1],
                        start_time: 1120,
                    },
                ],
            },
        });
        cy.get("span.count").contains("In 2 mins").should("exist");
    });
    it("playing now", () => {
        cy.mount(<Control />, {
            serverTime: { now: 1000 },
            room: {
                queue: [
                    {
                        ...queue[1],
                        start_time: 990,
                        track_duration: 60,
                    },
                ],
            },
        });
        cy.get("span.count").contains("Now").should("exist");
    });
});

function dnd(drag: string, drop: string) {
    const dataTransfer = new DataTransfer();

    cy.get(drag).trigger("dragstart", {
        dataTransfer,
    });

    cy.get(drop).trigger("drop", {
        dataTransfer,
    });
}
describe("drag & drop", () => {
    beforeEach(function () {
        cy.intercept("PUT", "/api/room/test/queue.json", (req) => {
            req.reply({
                body: {},
                //delay: 1000
            });
        }).as("move");
    });
    it("drag to top", () => {
        cy.mount(<Control />, {});
        dnd('[data-item-id="2"]', '[data-item-id="1"]');
        cy.wait("@move").then(({ request, response }) => {
            expect(response?.statusCode).to.eq(200);
            expect(request.body.source).to.eq(2);
            expect(request.body.target).to.eq(1);
        });
    });
    it("drag to bottom", () => {
        cy.mount(<Control />, {});
        dnd('[data-item-id="2"]', '[data-cy="end-marker"]');
        cy.wait("@move").then(({ request, response }) => {
            expect(response?.statusCode).to.eq(200);
            expect(request.body.source).to.eq(2);
            expect(request.body.target).to.eq(-1);
        });
        cy.contains("Shish").should("exist");
    });
});

describe("misc", () => {
    beforeEach(function () {
        cy.intercept("PUT", "/api/room/test/queue.json", (req) => {
            req.reply({ body: {}, delay: 1000 });
        }).as("move");
    });
    it("playground", () => {
        cy.mount(<Control />, {});
        cy.contains("READ ME :)").should("not.exist");
    });
});
