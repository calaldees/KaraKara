import { PageContext } from "@/providers/page";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { BackOr } from "./BackOr";

const meta = {
    title: "Components/BackOr",
    component: BackOr,
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof BackOr>;

export default meta;
type Story = StoryObj<typeof meta>;

export const WithBack: Story = {
    args: {
        to: "/test-room",
    },
    decorators: [
        (Story) => (
            <PageContext
                value={{
                    roomName: "test-room",
                    hasBack: true,
                    navigate: (() => {}) as any,
                }}
            >
                <Story />
            </PageContext>
        ),
    ],
};

export const WithoutBack: Story = {
    args: {
        to: "/test-room",
    },
    decorators: [
        (Story) => (
            <PageContext
                value={{
                    roomName: "test-room",
                    hasBack: false,
                    navigate: (() => {}) as any,
                }}
            >
                <Story />
            </PageContext>
        ),
    ],
};
