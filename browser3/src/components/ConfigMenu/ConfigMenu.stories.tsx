import { Screen } from "@/components";
import { ClientContext } from "@/providers/client";
import { PageContext } from "@/providers/page";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { ConfigMenu } from "./ConfigMenu";

const meta = {
    title: "Components/ConfigMenu",
    component: ConfigMenu,
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof ConfigMenu>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    parameters: {
        kkFullscreen: true,
        layout: "fullscreen",
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
                <ClientContext
                    value={
                        {
                            roomPassword: "",
                            setRoomPassword: () => {},
                            booth: false,
                            setBooth: () => {},
                            setShowSettings: () => {},
                        } as any
                    }
                >
                    <Screen title="test"></Screen>
                    <Story />
                </ClientContext>
            </PageContext>
        ),
    ],
};

export const WithPassword: Story = {
    decorators: [
        (Story) => (
            <PageContext
                value={{
                    roomName: "test-room",
                    hasBack: false,
                    navigate: (() => {}) as any,
                }}
            >
                <ClientContext
                    value={
                        {
                            roomPassword: "secret123",
                            setRoomPassword: () => {},
                            booth: false,
                            setBooth: () => {},
                            setShowSettings: () => {},
                        } as any
                    }
                >
                    <Story />
                </ClientContext>
            </PageContext>
        ),
    ],
};

export const BoothMode: Story = {
    decorators: [
        (Story) => (
            <PageContext
                value={{
                    roomName: "test-room",
                    hasBack: false,
                    navigate: (() => {}) as any,
                }}
            >
                <ClientContext
                    value={
                        {
                            roomPassword: "",
                            setRoomPassword: () => {},
                            booth: true,
                            setBooth: () => {},
                            setShowSettings: () => {},
                        } as any
                    }
                >
                    <Story />
                </ClientContext>
            </PageContext>
        ),
    ],
};

export const Fullscreen: Story = {
    decorators: [
        (Story) => (
            <PageContext
                value={{
                    roomName: "test-room",
                    hasBack: false,
                    navigate: (() => {}) as any,
                }}
            >
                <ClientContext
                    value={
                        {
                            roomPassword: "",
                            setRoomPassword: () => {},
                            booth: false,
                            setBooth: () => {},
                            setShowSettings: () => {},
                        } as any
                    }
                >
                    <Story />
                </ClientContext>
            </PageContext>
        ),
    ],
};

export const AllOptionsEnabled: Story = {
    decorators: [
        (Story) => (
            <PageContext
                value={{
                    roomName: "test-room",
                    hasBack: false,
                    navigate: (() => {}) as any,
                }}
            >
                <ClientContext
                    value={
                        {
                            roomPassword: "mypassword",
                            setRoomPassword: () => {},
                            booth: true,
                            setBooth: () => {},
                            setShowSettings: () => {},
                        } as any
                    }
                >
                    <Story />
                </ClientContext>
            </PageContext>
        ),
    ],
};
