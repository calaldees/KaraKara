import { List } from "@/components";
import type { Subtitle, Track } from "@/types";
import { createMockFetch } from "@/utils";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { LyricsViewer } from "./LyricsViewer";

const mockTrack: Track = {
    id: "track-1",
    duration: 180,
    tags: {
        title: ["Test Track"],
        category: ["Pop"],
    },
    attachments: {
        video: [],
        image: [],
        subtitle: [
            {
                variant: "Japanese",
                mime: "application/json",
                path: "w/WD2EV9q98n9.json",
            },
            {
                variant: "Japanese",
                mime: "text/vtt",
                path: "w/WD2EV9q98n9.vtt",
            },
            {
                variant: "English",
                mime: "application/json",
                path: "y/YciKFWK3xWQ.json",
            },
            { variant: "English", mime: "text/vtt", path: "y/YciKFWK3xWQ.vtt" },
        ],
    },
};
const mockEnglishLyrics: Subtitle[] = [
    { start: 0, end: 5, text: "And a one", top: false },
    { start: 5, end: 10, text: "And a two", top: false },
    { start: 10, end: 15, text: "And a one", top: false },
    { start: 15, end: 20, text: "Two three four", top: false },
];
const mockJapaneseLyrics: Subtitle[] = [
    { start: 0, end: 5, text: "いち", top: false },
    { start: 5, end: 10, text: "にい", top: false },
    { start: 10, end: 15, text: "さん", top: false },
    { start: 15, end: 20, text: "はい！", top: false },
];


const meta = {
    title: "Components/LyricsViewer",
    component: LyricsViewer,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
    argTypes: {
        variant: {
            control: "select",
            options: [...new Set(mockTrack.attachments.subtitle?.map(s => s.variant))],
            description: "Subtitle variant to display",
        },
    },
} satisfies Meta<typeof LyricsViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {
        track: mockTrack,
        variant: "Japanese",
        listItem: false,
    },
    beforeEach: () => {
        const originalFetch = window.fetch;
        window.fetch = createMockFetch({
            "w/WD2EV9q98n9.json": mockJapaneseLyrics,
            "y/YciKFWK3xWQ.json": mockEnglishLyrics,
        });
        return () => {
            window.fetch = originalFetch;
        };
    },
};

export const AsListItem: Story = {
    args: {
        track: mockTrack,
        variant: "English",
        listItem: true,
    },
    decorators: [
        (Story) => (
            <List>
                <Story />
            </List>
        ),
    ],
    beforeEach: () => {
        const originalFetch = window.fetch;
        window.fetch = createMockFetch({
            "w/WD2EV9q98n9.json": mockJapaneseLyrics,
            "y/YciKFWK3xWQ.json": mockEnglishLyrics,
        });
        return () => {
            window.fetch = originalFetch;
        };
    },
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
        variant: "English",
        listItem: false,
    },
};
