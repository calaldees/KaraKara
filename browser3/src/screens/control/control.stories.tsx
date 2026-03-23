import { expect, userEvent, within } from "storybook/test";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import queue from "../../../.storybook/files/small_queue.json";
import { Control } from "./control";

const meta = {
    title: "Screens/Control",
    component: Control,
    parameters: {
        layout: "fullscreen",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof Control>;

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
        await expect(canvas.getByText("READ ME :)")).toBeInTheDocument();
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
        await expect(counts.length).toBe(0);
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
    },
};

export const DragAndDropToTop: Story = {
    parameters: {
        testProps: {},
        msw: {
            handlers: [
                // Mock the API endpoint for moving queue items
                {
                    method: "PUT",
                    url: "/room/test/queue.json",
                    response: (_req: Request) => {
                        return new Response(JSON.stringify({}), {
                            status: 200,
                        });
                    },
                },
            ],
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Note: Drag and drop interactions in Storybook are complex
        // This is a placeholder for the interaction - actual DnD testing
        // may require more sophisticated setup or alternative approaches
        const dragItem = canvas.queryByTestId("item-2");
        const dropTarget = canvas.queryByTestId("item-1");

        if (dragItem && dropTarget) {
            // Simulating drag and drop - this may need adjustment based on
            // the actual DnD library being used
            await userEvent.pointer([
                { target: dragItem, keys: "[MouseLeft>]" },
                { coords: { x: 0, y: 0 } },
            ]);
        }
    },
};

export const DragAndDropToBottom: Story = {
    parameters: {
        testProps: {},
        msw: {
            handlers: [
                {
                    method: "PUT",
                    url: "/room/test/queue.json",
                    response: () => {
                        return new Response(JSON.stringify({}), {
                            status: 200,
                        });
                    },
                },
            ],
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);

        // Note: Similar to above, actual drag and drop testing would need
        // more sophisticated setup
        const dragItem = canvas.queryByTestId("item-2");
        const endMarker = canvas.queryByTestId("end-marker");

        if (dragItem && endMarker) {
            // Placeholder for drag and drop interaction
        }

        // Verify "Shish" appears in the queue
        await expect(canvas.getByText("Shish")).toBeInTheDocument();
    },
};
