import type { Track } from "@/types";
import type { Meta, StoryObj } from "@storybook/react";
import { TagsViewer } from "./TagsViewer";

const meta = {
    title: "Components/TagsViewer",
    component: TagsViewer,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof TagsViewer>;

export default meta;
type Story = StoryObj<typeof meta>;

const mockTrack: Track = {
    id: "track-1",
    duration: 213,
    tags: {
        title: ["Never Gonna Give You Up"],
        artist: ["Rick Astley"],
        album: ["Whenever You Need Somebody"],
        year: ["1987"],
        genre: ["Pop", "Dance"],
        language: ["English"],
        vocalist: ["Male"],
        from: ["Music Video"],
        source_type: ["Official"],
    },
    attachments: {
        video: [],
        image: [],
    },
};

export const Default: Story = {
    args: {
        track: mockTrack,
    },
};

export const MinimalTags: Story = {
    args: {
        track: {
            ...mockTrack,
            tags: {
                title: ["Simple Song"],
                artist: ["Unknown Artist"],
            },
        },
    },
};

export const ManyTags: Story = {
    args: {
        track: {
            ...mockTrack,
            tags: {
                title: ["Complex Track With Many Tags"],
                artist: ["Artist Name"],
                album: ["Album Name"],
                year: ["2024"],
                genre: ["Rock", "Alternative", "Indie"],
                language: ["English", "Japanese"],
                vocalist: ["Male", "Female"],
                mood: ["Energetic", "Upbeat", "Happy"],
                tempo: ["Fast"],
                instruments: ["Guitar", "Drums", "Bass", "Synthesizer"],
                series: ["Anime Series Name"],
                type: ["Opening", "Theme Song"],
                difficulty: ["Medium"],
                duration_category: ["Short"],
            },
        },
    },
};

export const AnimeTrack: Story = {
    args: {
        track: {
            ...mockTrack,
            tags: {
                title: ["Tank!"],
                artist: ["The Seatbelts"],
                series: ["Cowboy Bebop"],
                type: ["Opening"],
                genre: ["Jazz", "Blues"],
                language: ["Instrumental"],
                year: ["1998"],
                composer: ["Yoko Kanno"],
            },
        },
    },
};

export const MultipleValues: Story = {
    args: {
        track: {
            ...mockTrack,
            tags: {
                title: ["Collaboration Song"],
                artist: ["Artist One", "Artist Two", "Artist Three"],
                genre: ["Pop", "R&B", "Soul", "Electronic"],
                language: ["English", "Spanish", "French"],
            },
        },
    },
};
