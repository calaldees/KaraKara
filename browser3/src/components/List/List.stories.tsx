import { faEllipsisVertical, faPlay } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { List } from "./List";
import { ListItem } from "./ListItem";
import { Thumb } from "./Thumb";

const meta = {
    title: "Components/List",
    component: List,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof List>;

export default meta;
type Story = StoryObj<typeof meta>;

export const WithBasicItems: Story = {
    args: {
        children: (
            <>
                <ListItem title="Item 1" info="Additional info" />
                <ListItem title="Item 2" info="More details" />
                <ListItem title="Item 3" info="Even more info" />
            </>
        ),
    },
};

export const WithCounts: Story = {
    args: {
        children: (
            <>
                <ListItem title="Songs" count={42} />
                <ListItem title="Artists" count={15} />
                <ListItem title="Albums" count={8} />
            </>
        ),
    },
};

export const WithThumbs: Story = {
    args: {
        children: (
            <>
                <ListItem
                    thumb={<Thumb track={undefined} />}
                    title="Track with thumbnail"
                    info="Artist Name"
                />
                <ListItem
                    thumb={<Thumb track={undefined} />}
                    title="Another track"
                    info="Another artist"
                />
            </>
        ),
    },
};

export const WithActions: Story = {
    args: {
        children: (
            <>
                <ListItem
                    title="Track 1"
                    info="Artist - Album"
                    action={<FAIcon icon={faPlay} />}
                />
                <ListItem
                    title="Track 2"
                    info="Artist - Album"
                    action={<FAIcon icon={faPlay} />}
                />
                <ListItem
                    title="Track 3"
                    info="Artist - Album"
                    action={<FAIcon icon={faPlay} />}
                />
            </>
        ),
    },
};

export const ComplexListItems: Story = {
    args: {
        children: (
            <>
                <ListItem
                    thumb={<Thumb track={undefined} dragHandle={true} />}
                    title="Never Gonna Give You Up"
                    info="Rick Astley • Whenever You Need Somebody"
                    count="3:33"
                    action={<FAIcon icon={faEllipsisVertical} />}
                />
                <ListItem
                    thumb={<Thumb track={undefined} dragHandle={true} />}
                    title="Bohemian Rhapsody"
                    info="Queen • A Night at the Opera"
                    count="5:55"
                    action={<FAIcon icon={faEllipsisVertical} />}
                />
                <ListItem
                    thumb={<Thumb track={undefined} dragHandle={true} />}
                    title="Don't Stop Believin'"
                    info="Journey • Escape"
                    count="4:09"
                    action={<FAIcon icon={faEllipsisVertical} />}
                />
            </>
        ),
    },
};

export const Empty: Story = {
    args: {
        children: null,
    },
};
