import type { Meta, StoryObj } from "storybook-react-rsbuild";
import type { Track } from "@/types";
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
    id: "Bad_Apple",
    duration: 219.1,
    attachments: {
        video: [
            {
                variant: "Instrumental",
                mime: "video/webm; codecs=av01.0.05M.08,opus",
                path: "8/879pGGQNP9J.webm",
            },
            {
                variant: "Vocal",
                mime: "video/webm; codecs=av01.0.05M.08,opus",
                path: "a/A4u4GAwwyfZ.webm",
            },
            {
                variant: "Instrumental",
                mime: "video/mp4; codecs=avc1.4D401E,mp4a.40.2",
                path: "j/j0KzEi2Vb_b.mp4",
            },
            {
                variant: "Vocal",
                mime: "video/mp4; codecs=avc1.4D401E,mp4a.40.2",
                path: "x/x_ac4YGd_3W.mp4",
            },
        ],
        image: [
            {
                variant: "Instrumental",
                mime: "image/avif",
                path: "i/Ib0f3UwSS58.avif",
            },
            {
                variant: "Vocal",
                mime: "image/avif",
                path: "v/VxY3lrigg2F.avif",
            },
        ],
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
    tags: {
        category: ["game"],
        from: ["Touhou"],
        Touhou: ["Gensoukyou ~ Lotus Land Story"],
        title: ["Bad Apple"],
        artist: ["Nomico", "ZUN"],
        use: ["doujin"],
        vocaltrack: ["off", "on"],
        length: ["full"],
        lang: ["jp"],
        vocalstyle: ["female"],
        genre: ["dance", "pop"],
        contributor: ["choco"],
        date: ["2007-05-20"],
        subs: ["soft"],
        source_type: ["video"],
        aspect_ratio: ["4:3"],
        duration: ["3m39s"],
        year: ["2007"],
    },
};

export const VocalEnglish: Story = {
    args: {
        track: mockTrack,
        videoVariant: "Vocal",
        subtitleVariant: "English",
    },
};

export const InstrumentalJapanese: Story = {
    args: {
        track: mockTrack,
        videoVariant: "Instrumental",
        subtitleVariant: "Japanese",
    },
};
