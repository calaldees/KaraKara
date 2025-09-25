import * as utils from "@/utils";
import timezone_mock from "timezone-mock";
import { afterEach, describe, expect, test } from "vitest";

describe("short_date", () => {
    afterEach(() => {
        timezone_mock.unregister();
    });
    test("with no timezone, assume local", () => {
        // whatever timezone runs this unit test, the time should be the same
        expect(utils.short_date("2023-08-14T12:00:00")).toEqual("12:00");

        timezone_mock.register("UTC");
        expect(utils.short_date("2023-08-14T12:00:00")).toEqual("12:00");

        timezone_mock.register("Australia/Adelaide");
        expect(utils.short_date("2023-08-14T12:00:00")).toEqual("12:00");
    });
    test("display timezone'd timestamps in local time", () => {
        // if the timestamp is UTC (+00:00) and we are in UTC,
        // then the time should be the same
        timezone_mock.register("UTC");
        expect(utils.short_date("2023-08-14T12:00:00+00:00")).toEqual("12:00");

        // If the timestamp is +1, our display should be -1
        timezone_mock.register("UTC");
        expect(utils.short_date("2023-08-14T12:00:00+01:00")).toEqual("11:00");

        // If we are in +1, our display should be +1
        timezone_mock.register("Europe/London");
        expect(utils.short_date("2023-08-14T12:00:00+00:00")).toEqual("13:00");

        // if the timestamp is in New York (-04:00) and we are in Adelaide (+09:30),
        // then the time should be +1330
        timezone_mock.register("Australia/Adelaide");
        expect(utils.short_date("2023-08-14T12:00:00-04:00")).toEqual("01:30");
    });
});
