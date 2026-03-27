import { queue, settings } from "@/utils/test_data";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { expect, within } from "storybook/test";
import Queue from "./queue";

const meta = {
    title: "Screens/Queue",
    component: Queue,
    parameters: {
        kkFullscreen: true,
        layout: "fullscreen",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof Queue>;

export default meta;
type Story = StoryObj<typeof meta>;

export const NoTracks: Story = {
    parameters: {
        testProps: {
            room: {
                queue: [],
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await expect(canvas.getByText("Queue Empty")).toBeInTheDocument();
        await expect(canvas.queryByText("Coming Soon")).not.toBeInTheDocument();
    },
};

export const NowPlayingNoTime: Story = {
    parameters: {
        testProps: {
            serverTime: { now: 1000 },
            room: {
                queue: [
                    {
                        ...queue[1],
                        start_time: null,
                    },
                ],
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        const counts = canvas.queryAllByText(/^(In|Now)/);
        await expect(counts.length).toBe(1); // "Now Playing" is the screen title
        await expect(canvas.queryByText("Coming Soon")).not.toBeInTheDocument();
    },
};

export const NowPlayingInTheFuture: Story = {
    parameters: {
        testProps: {
            serverTime: { now: 1000 },
            room: {
                queue: [
                    {
                        ...queue[1],
                        start_time: 1120,
                    },
                ],
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await expect(canvas.getByText("In 2 mins")).toBeInTheDocument();
        await expect(canvas.queryByText("Coming Soon")).not.toBeInTheDocument();
    },
};

export const NowPlayingNow: Story = {
    parameters: {
        testProps: {
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
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await expect(canvas.getByText("Now")).toBeInTheDocument();
        await expect(canvas.queryByText("Coming Soon")).not.toBeInTheDocument();
    },
};

export const ComingSoonDisabled: Story = {
    parameters: {
        testProps: {
            room: {
                settings: {
                    ...settings,
                    coming_soon_track_count: 0,
                },
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await expect(canvas.queryByText("Coming Soon")).not.toBeInTheDocument();
    },
};

export const ComingLater: Story = {
    parameters: {
        testProps: {},
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await expect(canvas.getByText("Coming Later")).toBeInTheDocument();
    },
};

export const MyEntriesWithEntries: Story = {
    parameters: {
        testProps: {
            client: { performerName: "Alice" },
            room: {
                queue: [
                    {
                        ...queue[1],
                        session_id: "session",
                    },
                ],
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await expect(canvas.getByText("My Entries")).toBeInTheDocument();
    },
};

export const MyEntriesWithoutEntries: Story = {
    parameters: {
        testProps: {
            client: { performerName: "Zazzy" },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        await expect(canvas.queryByText("My Entries")).not.toBeInTheDocument();
    },
};
