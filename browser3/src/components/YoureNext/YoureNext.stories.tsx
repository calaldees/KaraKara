import { ClientContext } from "@/providers/client";
import { ServerContext } from "@/providers/server";
import type { QueueItem, Track } from "@/types";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { YoureNext } from "./YoureNext";

const meta = {
    title: "Components/YoureNext",
    component: YoureNext,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof YoureNext>;

export default meta;
type Story = StoryObj<typeof meta>;

const mockTracks: Record<string, Track> = {
    "track-1": {
        id: "track-1",
        duration: 213,
        tags: {
            title: ["Never Gonna Give You Up"],
            artist: ["Rick Astley"],
        },
        attachments: {
            video: [],
            image: [],
        },
    },
    "track-2": {
        id: "track-2",
        duration: 180,
        tags: {
            title: ["Bohemian Rhapsody"],
            artist: ["Queen"],
        },
        attachments: {
            video: [],
            image: [],
        },
    },
    "track-3": {
        id: "track-3",
        duration: 195,
        tags: {
            title: ["Take On Me"],
            artist: ["a-ha"],
        },
        attachments: {
            video: [],
            image: [],
        },
    },
};

const createQueueItem = (
    id: number,
    trackId: string,
    performerName: string,
    sessionId: string,
): QueueItem => ({
    id,
    performer_name: performerName,
    session_id: sessionId,
    start_time: Date.now() / 1000,
    track_duration: mockTracks[trackId].duration,
    track_id: trackId,
    video_variant: "default",
    subtitle_variant: "default",
});

export const YourSongIsUpNow: Story = {
    args: {
        queue: [
            createQueueItem(1, "track-1", "Current User", "session-123"),
            createQueueItem(2, "track-2", "Another User", "session-456"),
            createQueueItem(3, "track-3", "Third User", "session-789"),
        ],
    },
    decorators: [
        (Story) => {
            // Mock the useApi hook by setting the session cookie
            document.cookie = "kksid=session-123";
            return (
                <ServerContext value={{ tracks: mockTracks } as any}>
                    <ClientContext
                        value={{ performerName: "Current User" } as any}
                    >
                        <Story />
                    </ClientContext>
                </ServerContext>
            );
        },
    ],
};

export const YourSongIsUpNext: Story = {
    args: {
        queue: [
            createQueueItem(1, "track-2", "Another User", "session-456"),
            createQueueItem(2, "track-1", "Current User", "session-123"),
            createQueueItem(3, "track-3", "Third User", "session-789"),
        ],
    },
    decorators: [
        (Story) => {
            document.cookie = "kksid=session-123";
            return (
                <ServerContext value={{ tracks: mockTracks } as any}>
                    <ClientContext
                        value={{ performerName: "Current User" } as any}
                    >
                        <Story />
                    </ClientContext>
                </ServerContext>
            );
        },
    ],
};

export const NoUserSongs: Story = {
    args: {
        queue: [
            createQueueItem(1, "track-2", "Another User", "session-456"),
            createQueueItem(2, "track-3", "Third User", "session-789"),
        ],
    },
    decorators: [
        (Story) => {
            document.cookie = "kksid=session-123";
            return (
                <ServerContext value={{ tracks: mockTracks } as any}>
                    <ClientContext
                        value={{ performerName: "Current User" } as any}
                    >
                        <Story />
                    </ClientContext>
                </ServerContext>
            );
        },
    ],
};

export const EmptyQueue: Story = {
    args: {
        queue: [],
    },
    decorators: [
        (Story) => {
            document.cookie = "kksid=session-123";
            return (
                <ServerContext value={{ tracks: mockTracks } as any}>
                    <ClientContext
                        value={{ performerName: "Current User" } as any}
                    >
                        <Story />
                    </ClientContext>
                </ServerContext>
            );
        },
    ],
};

export const MatchByPerformerName: Story = {
    args: {
        queue: [
            createQueueItem(1, "track-2", "Another User", "session-456"),
            createQueueItem(2, "track-1", "Current User", "session-different"),
            createQueueItem(3, "track-3", "Third User", "session-789"),
        ],
    },
    decorators: [
        (Story) => {
            document.cookie = "kksid=session-123";
            return (
                <ServerContext value={{ tracks: mockTracks } as any}>
                    <ClientContext
                        value={{ performerName: "Current User" } as any}
                    >
                        <Story />
                    </ClientContext>
                </ServerContext>
            );
        },
    ],
};
