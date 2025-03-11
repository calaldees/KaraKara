/// <reference types="cypress" />
/// <reference path="../../../cypress/support/component.ts" />

import { Queue } from "../queue";
import tracks from "../../../cypress/fixtures/small_tracks.json";
import queue from "../../../cypress/fixtures/small_queue.json";
import settings from "../../../cypress/fixtures/small_settings.json";

describe("no tracks", () => {
    it("no tracks", () => {
        cy.mount(<Queue />, {
            client: {},
            server: {},
            room: {
                queue: [],
            },
        });
        cy.contains("Queue Empty").should("exist");
        cy.contains("Coming Soon").should("not.exist");
    });
});

describe("now playing", () => {
    it("no time", () => {
        cy.mount(<Queue />, {
            client: {},
            server: {
                now: 1000,
            },
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
        cy.contains("Coming Soon").should("not.exist");
    });
    it("in the future", () => {
        cy.mount(<Queue />, {
            client: {},
            server: {
                now: 1000,
            },
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
        cy.contains("Coming Soon").should("not.exist");
    });
    it("playing now", () => {
        cy.mount(<Queue />, {
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
                    },
                ],
            },
        });
        cy.get("span.count").contains("Now").should("exist");
        cy.contains("Coming Soon").should("not.exist");
    });
    it("with lyrics", () => {
        const track_2_with_lyrics: Track = {
            ...tracks["track_id_2"],
            lyrics: ["foo", "bar", "baz"],
        };
        cy.mount(<Queue />, {
            client: {},
            server: {
                now: 1000,
                tracks: {
                    ...tracks,
                    track_id_2: track_2_with_lyrics,
                },
            },
            room: {
                queue: [queue[1]],
            },
        });
        cy.contains("baz").should("exist");
    });
});

describe("coming soon", () => {
    it("coming soon disabled", () => {
        cy.mount(<Queue />, {
            client: {},
            server: {},
            room: {
                settings: {
                    ...settings,
                    coming_soon_track_count: 0,
                },
            },
        });
        cy.contains("Coming Soon").should("not.exist");
    });
});

describe("coming later", () => {
    // FIXME: test order
    it("coming later", () => {
        cy.mount(<Queue />, {
            client: {},
            server: {},
            room: {},
        });
        cy.contains("Coming Later").should("exist");
    });
});

describe("my entries", () => {
    it("with entries", () => {
        cy.mount(<Queue />, {
            client: {},
            server: {},
            room: {},
        });
        cy.contains("My Entries").should("exist");
    });
    it("without entries", () => {
        cy.mount(<Queue />, {
            client: { performerName: "Zazzy" },
            server: {},
            room: { sessionId: "nobody" },
        });
        cy.contains("My Entries").should("not.exist");
    });
});

describe("misc", () => {
    it("playground", () => {
        cy.mount(<Queue />, {
            client: {},
            server: {},
            room: {},
        });
    });
});
