import { faPlay } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { ButtonRow } from "./ButtonRow";

const meta = {
    title: "Components/ButtonRow",
    component: ButtonRow,
    parameters: {
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof ButtonRow>;

export default meta;
type Story = StoryObj<typeof meta>;

export const SingleButton: Story = {
    args: {
        children: <button>Single Button</button>,
    },
};

export const ManyButtons: Story = {
    args: {
        children: (
            <>
                <button>Action 1</button>
                <a className="button">Action 2</a>
                <button>
                    <FAIcon icon={faPlay} />
                </button>
                <button>Action 4</button>
                <button disabled={true}>Action 5</button>
            </>
        ),
    },
};
