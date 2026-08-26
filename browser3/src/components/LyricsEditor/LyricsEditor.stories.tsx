import type { Subtitle } from "@/types";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { LyricsEditor } from "./LyricsEditor";

const meta = {
    title: "Components/LyricsEditor",
    component: LyricsEditor,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof LyricsEditor>;

export default meta;
type Story = StoryObj<typeof meta>;

// Mock subtitle data
const mockEnglishLyrics: Subtitle[] = [
    { start: 0, end: 5, text: "Never gonna give you up", top: false },
    { start: 5, end: 10, text: "Never gonna let you down", top: false },
    { start: 10, end: 15, text: "Never gonna run around", top: false },
    { start: 15, end: 20, text: "And desert you", top: false },
];

const mockJapaneseLyrics: Subtitle[] = [
    { start: 0, end: 5, text: "君をあきらめない", top: false },
    { start: 5, end: 10, text: "君を失望させない", top: false },
    { start: 10, end: 15, text: "走り回って", top: false },
    { start: 15, end: 20, text: "君を見捨てたりしない", top: false },
];

const mockDualLyrics: Subtitle[] = [
    { start: 0, end: 5, text: "English lyrics on bottom", top: false },
    { start: 0, end: 5, text: "日本語の歌詞は上に", top: true },
    { start: 5, end: 10, text: "Second line below", top: false },
    { start: 5, end: 10, text: "2行目が上", top: true },
    { start: 10, end: 15, text: "Third line here", top: false },
    { start: 10, end: 15, text: "3行目はこちら", top: true },
];

const mockKaraokeLyrics: Subtitle[] = [
    { start: 0, end: 2.5, text: "We're no strangers to love", top: false },
    { start: 2.5, end: 5, text: "You know the rules and so do I", top: false },
    {
        start: 5,
        end: 7.5,
        text: "A full commitment's what I'm thinking of",
        top: false,
    },
    {
        start: 7.5,
        end: 10,
        text: "You wouldn't get this from any other guy",
        top: false,
    },
    {
        start: 10,
        end: 12,
        text: "I just wanna tell you how I'm feeling",
        top: false,
    },
    { start: 12, end: 14, text: "Gotta make you understand", top: false },
];

export const EnglishLyrics: Story = {
    args: {
        lines: mockEnglishLyrics,
        onChanged: (lines) => console.log("Lyrics changed", lines),
    },
};

export const JapaneseLyrics: Story = {
    args: {
        lines: mockJapaneseLyrics,
        onChanged: (lines) => console.log("Lyrics changed", lines),
    },
};

export const DualLanguage: Story = {
    args: {
        lines: mockDualLyrics,
        onChanged: (lines) => console.log("Lyrics changed", lines),
    },
};

export const KaraokeStyle: Story = {
    args: {
        lines: mockKaraokeLyrics,
        onChanged: (lines) => console.log("Lyrics changed", lines),
    },
};

export const EmptySubtitles: Story = {
    args: {
        lines: [],
        onChanged: (lines) => console.log("Lyrics changed", lines),
    },
};

export const NoSubtitleAttachment: Story = {
    args: {
        lines: [],
        onChanged: (lines) => console.log("Lyrics changed", lines),
    },
};

export const SingleSubtitle: Story = {
    args: {
        lines: [{ start: 0, end: 5, text: "Just one line", top: false }],
        onChanged: (lines) => console.log("Lyrics changed", lines),
    },
};

export const PreciseTimings: Story = {
    args: {
        lines: [
            { start: 0.25, end: 1.75, text: "Precise start time", top: false },
            {
                start: 1.75,
                end: 3.33,
                text: "And precise end time",
                top: false,
            },
            {
                start: 3.33,
                end: 5.99,
                text: "With decimal seconds",
                top: false,
            },
        ],
        onChanged: (lines) => console.log("Lyrics changed", lines),
    },
};
