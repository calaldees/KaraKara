import type { Track } from "@/types";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { VideoPreview } from "./VideoPreview";

const meta = {
    title: "Components/VideoPreview",
    component: VideoPreview,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof VideoPreview>;

export default meta;
type Story = StoryObj<typeof meta>;

const mockTrack: Track = {
    id: "track-1",
    duration: 213,
    tags: {
        title: ["Big Buck Bunny"],
        category: ["Animation"],
    },
    attachments: {
        video: [
            {
                variant: "default",
                mime: "video/mp4",
                path: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            },
        ],
        image: [
            {
                variant: "default",
                mime: "image/jpeg",
                path: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/images/BigBuckBunny.jpg",
            },
        ],
        subtitle: [
            {
                variant: "english",
                mime: "text/vtt",
                path: "https://example.com/subtitles.vtt",
            },
        ],
    },
};

export const Default: Story = {
    args: {
        track: mockTrack,
        videoVariant: "default",
        subtitleVariant: "english",
    },
};

export const WithoutSubtitles: Story = {
    args: {
        track: mockTrack,
        videoVariant: "default",
        subtitleVariant: null,
    },
};

export const NoSubtitleVariant: Story = {
    args: {
        track: mockTrack,
        videoVariant: "default",
        subtitleVariant: null,
    },
};

export const MultipleVideoVariants: Story = {
    args: {
        track: {
            ...mockTrack,
            attachments: {
                ...mockTrack.attachments,
                video: [
                    {
                        variant: "sd",
                        mime: "video/mp4",
                        path: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                    },
                    {
                        variant: "hd",
                        mime: "video/mp4",
                        path: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                    },
                    {
                        variant: "default",
                        mime: "video/webm",
                        path: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
                    },
                ],
            },
        },
        videoVariant: "hd",
        subtitleVariant: "english",
    },
};

export const NullVideoVariant: Story = {
    args: {
        track: mockTrack,
        videoVariant: null,
        subtitleVariant: "english",
    },
};

export const WithPoster: Story = {
    args: {
        track: {
            ...mockTrack,
            attachments: {
                ...mockTrack.attachments,
                image: [
                    {
                        variant: "default",
                        mime: "image/jpeg",
                        path: "https://via.placeholder.com/640x360/0066cc/ffffff?text=Video+Poster",
                    },
                ],
            },
        },
        videoVariant: "default",
        subtitleVariant: null,
    },
};
