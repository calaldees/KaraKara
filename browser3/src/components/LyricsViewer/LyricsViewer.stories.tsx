import { List } from "@/components";
import type { Track } from "@/types";
import { tracks } from "@/utils/test_data";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { LyricsViewer } from "./LyricsViewer";

const mockTrack: Track = tracks["track_id_1"];

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
            options: [
                ...new Set(
                    mockTrack.attachments.subtitle?.map((s) => s.variant),
                ),
            ],
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
