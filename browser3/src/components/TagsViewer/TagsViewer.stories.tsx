import type { Track } from "@/types";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { TagsViewer } from "./TagsViewer";
import { within, expect } from "storybook/test";

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
        duration: ["260"],
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

export const SpecialTags: Story = {
    args: {
        track: {
            ...mockTrack,
            tags: {
                title: ["Special Tags Example"],
                source: ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
                duration: ["213"],
            },
        },
    },
    play: async ({ canvasElement }) => {
        const canvas = within(canvasElement);
        //const sourceLink = await canvas.findByText("YouTube");
        //expect(sourceLink).toBeInTheDocument();
        //expect(sourceLink).toHaveAttribute("href", "https://www.youtube.com/watch?v=dQw4w9WgXcQ");

        const durationTag = await canvas.findByText("3m33s");
        await expect(durationTag).toBeInTheDocument();
    }
};
