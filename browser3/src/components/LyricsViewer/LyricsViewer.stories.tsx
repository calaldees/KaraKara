import type { Subtitle, Track } from "@/types";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { LyricsViewer } from "./LyricsViewer";

const meta = {
    title: "Components/LyricsViewer",
    component: LyricsViewer,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof LyricsViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

const mockTrack: Track = {
    id: "track-1",
    duration: 180,
    tags: {
        title: ["Never Gonna Give You Up"],
        category: ["Pop"],
    },
    attachments: {
        video: [],
        image: [],
        subtitle: [
            {
                variant: "english",
                mime: "application/json",
                path: "/lyrics.json",
            },
        ],
    },
};

const mockLyrics: Subtitle[] = [
    { start: 0, end: 5, text: "We're no strangers to love", top: false },
    { start: 5, end: 10, text: "You know the rules and so do I", top: false },
    {
        start: 10,
        end: 15,
        text: "A full commitment's what I'm thinking of",
        top: false,
    },
    {
        start: 15,
        end: 20,
        text: "You wouldn't get this from any other guy",
        top: false,
    },
    {
        start: 20,
        end: 25,
        text: "I just wanna tell you how I'm feeling",
        top: false,
    },
    { start: 25, end: 30, text: "Gotta make you understand", top: false },
    { start: 30, end: 35, text: "Never gonna give you up", top: true },
    { start: 35, end: 40, text: "Never gonna let you down", top: true },
    {
        start: 40,
        end: 45,
        text: "Never gonna run around and desert you",
        top: true,
    },
];

export const Default: Story = {
    args: {
        track: mockTrack,
        variant: "english",
        listItem: false,
    },
    decorators: [
        (Story) => {
            // Mock fetch for lyrics
            const originalFetch = global.fetch;
            global.fetch = () => {
                return Promise.resolve({
                    json: () => Promise.resolve(mockLyrics),
                } as Response);
            };

            document.cookie = "kksid=session-123";

            const result = <Story />;

            // Restore fetch
            global.fetch = originalFetch;

            return result;
        },
    ],
};

export const AsListItem: Story = {
    args: {
        track: mockTrack,
        variant: "english",
        listItem: true,
    },
    decorators: [
        (Story) => {
            const originalFetch = global.fetch;
            global.fetch = () => {
                return Promise.resolve({
                    json: () => Promise.resolve(mockLyrics),
                } as Response);
            };

            document.cookie = "kksid=session-123";

            const result = (
                <ul>
                    <Story />
                </ul>
            );

            global.fetch = originalFetch;

            return result;
        },
    ],
};

export const NoLyrics: Story = {
    args: {
        track: {
            ...mockTrack,
            attachments: {
                ...mockTrack.attachments,
                subtitle: [],
            },
        },
        variant: "english",
        listItem: false,
    },
    decorators: [
        (Story) => {
            document.cookie = "kksid=session-123";
            return <Story />;
        },
    ],
};
