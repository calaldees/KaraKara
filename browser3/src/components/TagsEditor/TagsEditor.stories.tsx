import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { TagsEditor } from "./TagsEditor";

const meta = {
    title: "Components/TagsEditor",
    component: TagsEditor,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof TagsEditor>;

export default meta;
type Story = StoryObj<typeof meta>;

// Common possible values for checkbox fields
const commonPossibleValues: Record<string, string[]> = {
    category: [
        "Pop",
        "Rock",
        "Jazz",
        "Anime",
        "Opera",
        "Alternative",
        "Indie",
        "R&B",
    ],
    use: ["Opening", "Ending", "Insert", "Theme Song"],
    vocaltrack: ["Vocal", "Instrumental", "Off Vocal"],
    vocalstyle: ["Male", "Female", "Duet", "Group"],
    lang: ["English", "Japanese", "Spanish", "Instrumental", "Korean"],
};

export const Default: Story = {
    args: {
        tags: {
            title: ["Never Gonna Give You Up"],
            artist: ["Rick Astley"],
            album: ["Whenever You Need Somebody"],
            category: ["Pop"],
            vocaltrack: ["Vocal"],
            vocalstyle: ["Male"],
            lang: ["English"],
            released: ["1987-07-27"],
        },
        possibleValuesByKey: commonPossibleValues,
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};

export const RockSong: Story = {
    args: {
        tags: {
            title: ["Bohemian Rhapsody"],
            artist: ["Queen"],
            album: ["A Night at the Opera"],
            category: ["Rock", "Opera"],
            vocaltrack: ["Vocal"],
            vocalstyle: ["Male"],
            lang: ["English"],
            released: ["1975-10-31"],
        },
        possibleValuesByKey: commonPossibleValues,
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};

export const AnimeTrack: Story = {
    args: {
        tags: {
            title: ["Tank!"],
            artist: ["The Seatbelts"],
            composer: ["Yoko Kanno"],
            series: ["Cowboy Bebop"],
            category: ["Jazz", "Anime"],
            use: ["Opening"],
            vocaltrack: ["Instrumental"],
            lang: ["Instrumental"],
            released: ["1998-04-03"],
        },
        possibleValuesByKey: commonPossibleValues,
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};

export const MinimalTags: Story = {
    args: {
        tags: {
            title: ["Simple Song"],
            artist: ["Unknown Artist"],
        },
        possibleValuesByKey: commonPossibleValues,
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};

export const ManyTags: Story = {
    args: {
        tags: {
            title: ["Complex Track With Many Tags"],
            artist: ["Artist Name", "Featured Artist"],
            album: ["Album Name"],
            composer: ["Composer One", "Composer Two"],
            lyricist: ["Lyricist Name"],
            series: ["Anime Series Name"],
            category: ["Rock", "Alternative", "Indie"],
            use: ["Opening", "Theme Song"],
            vocaltrack: ["Vocal"],
            vocalstyle: ["Male", "Female"],
            lang: ["English", "Japanese"],
            released: ["2024-01-15"],
            mood: ["Energetic", "Upbeat"],
            tempo: ["Fast"],
        },
        possibleValuesByKey: commonPossibleValues,
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};

export const MultipleArtists: Story = {
    args: {
        tags: {
            title: ["Collaboration Song"],
            artist: ["Artist One", "Artist Two", "Artist Three"],
            category: ["Pop", "R&B"],
            vocaltrack: ["Vocal"],
            vocalstyle: ["Male", "Female"],
            lang: ["English", "Spanish"],
            released: ["2023-06-15"],
        },
        possibleValuesByKey: commonPossibleValues,
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};

export const DateTagsOnly: Story = {
    args: {
        tags: {
            title: ["Track With Date Tags"],
            artist: ["Test Artist"],
            released: ["2020-01-15"],
            added: ["2024-03-20"],
            updated: ["2024-12-01"],
        },
        possibleValuesByKey: commonPossibleValues,
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};

export const EmptyTags: Story = {
    args: {
        tags: {},
        possibleValuesByKey: commonPossibleValues,
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};

export const LimitedPossibleValues: Story = {
    args: {
        tags: {
            title: ["Test Song"],
            artist: ["Test Artist"],
            category: ["Pop"],
            lang: ["English"],
        },
        possibleValuesByKey: {
            category: ["Pop", "Rock"],
            use: ["Opening"],
            vocaltrack: ["Vocal"],
            vocalstyle: ["Male"],
            lang: ["English", "Japanese"],
        },
        onChanged: (tagKey, newValues) =>
            console.log(`Tag ${tagKey} changed to`, newValues),
    },
};
