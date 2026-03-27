import { RoomContext } from "@/providers/room";
import type { QueueItem } from "@/types";
import { ServerTimeContext } from "@shish2k/react-use-servertime";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { EventProgressBar } from "./EventProgressBar";

const meta = {
    title: "Components/EventProgressBar",
    component: EventProgressBar,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof EventProgressBar>;

export default meta;
type Story = StoryObj<typeof meta>;

const mockQueueItem: QueueItem = {
    id: 1,
    performer_name: "Test User",
    session_id: "session-123",
    start_time: Date.now() / 1000,
    track_duration: 180,
    track_id: "track-1",
    video_variant: "default",
    subtitle_variant: "default",
};

const startTime = new Date("2024-01-01T18:00:00Z").getTime() / 1000;
const nowTime = new Date("2024-01-01T19:30:00Z").getTime() / 1000;
const queueEndTime = nowTime + 3600; // 1 hour from now
const endTime = new Date("2024-01-01T22:00:00Z").getTime() / 1000;

export const Default: Story = {
    decorators: [
        (Story) => (
            <RoomContext
                value={
                    {
                        fullQueue: [
                            { ...mockQueueItem, start_time: nowTime },
                            {
                                ...mockQueueItem,
                                id: 2,
                                start_time: queueEndTime,
                            },
                        ],
                        settings: {
                            validation_event_start_datetime: new Date(
                                startTime * 1000,
                            ).toISOString(),
                            validation_event_end_datetime: new Date(
                                endTime * 1000,
                            ).toISOString(),
                        },
                    } as any
                }
            >
                <ServerTimeContext
                    value={{
                        now: nowTime,
                        offset: 0,
                        tweak: 1,
                        setTweak: () => {},
                    }}
                >
                    <Story />
                </ServerTimeContext>
            </RoomContext>
        ),
    ],
};

export const EventAlmostOver: Story = {
    decorators: [
        (Story) => (
            <RoomContext
                value={
                    {
                        fullQueue: [
                            { ...mockQueueItem, start_time: nowTime },
                            {
                                ...mockQueueItem,
                                id: 2,
                                start_time: nowTime + 300,
                            },
                        ],
                        settings: {
                            validation_event_start_datetime: new Date(
                                startTime * 1000,
                            ).toISOString(),
                            validation_event_end_datetime: new Date(
                                (nowTime + 600) * 1000,
                            ).toISOString(),
                        },
                    } as any
                }
            >
                <ServerTimeContext
                    value={{
                        now: nowTime,
                        offset: 0,
                        tweak: 1,
                        setTweak: () => {},
                    }}
                >
                    <Story />
                </ServerTimeContext>
            </RoomContext>
        ),
    ],
};

export const EventJustStarted: Story = {
    decorators: [
        (Story) => (
            <RoomContext
                value={
                    {
                        fullQueue: [
                            { ...mockQueueItem, start_time: nowTime },
                            {
                                ...mockQueueItem,
                                id: 2,
                                start_time: nowTime + 7200,
                            },
                        ],
                        settings: {
                            validation_event_start_datetime: new Date(
                                (nowTime - 300) * 1000,
                            ).toISOString(),
                            validation_event_end_datetime: new Date(
                                (nowTime + 14400) * 1000,
                            ).toISOString(),
                        },
                    } as any
                }
            >
                <ServerTimeContext
                    value={{
                        now: nowTime,
                        offset: 0,
                        tweak: 1,
                        setTweak: () => {},
                    }}
                >
                    <Story />
                </ServerTimeContext>
            </RoomContext>
        ),
    ],
};
