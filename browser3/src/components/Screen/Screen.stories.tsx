import { faArrowLeft, faCog } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { ButtonRow } from "../ButtonRow/ButtonRow";
import { Screen } from "./Screen";

const meta = {
    title: "Components/Screen",
    component: Screen,
    parameters: {
        kkFullscreen: true,
        layout: "fullscreen",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof Screen>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {
        title: "Screen Title",
        children: (
            <div>
                <p>This is the main content area of the screen.</p>
                <p>It can contain any components or elements.</p>
            </div>
        ),
    },
};

export const CompleteExample: Story = {
    args: {
        title: "Complete Screen Example",
        className: "example-screen",
        navLeft: <FAIcon icon={faArrowLeft} />,
        navRight: <FAIcon icon={faCog} />,
        footer: (
            <ButtonRow>
                <button style={{ flex: 1 }}>Cancel</button>
                <button style={{ flex: 1 }}>Save</button>
            </ButtonRow>
        ),
        children: (
            <div>
                <h2>Content Section</h2>
                <p>
                    This example demonstrates all available props for the Screen
                    component.
                </p>
                <ul>
                    <li>Title in header</li>
                    <li>Left navigation</li>
                    <li>Right navigation</li>
                    <li>Main content area (scrollable)</li>
                    <li>Footer with actions</li>
                </ul>
            </div>
        ),
    },
};

export const PairedScreenExample: Story = {
    args: {
        title: "moo",
    },
    render: () => (
        <div id="page">
            <Screen title="Left Screen">
                <p>This is the left screen content.</p>
            </Screen>
            <Screen
                title="Right Screen"
                navLeft={<FAIcon icon={faArrowLeft} />}
                navRight={<FAIcon icon={faCog} />}
                footer={
                    <ButtonRow>
                        <button>Cancel</button>
                        <button>Save</button>
                    </ButtonRow>
                }
            >
                <p>This is the right screen content.</p>
            </Screen>
        </div>
    ),
};
