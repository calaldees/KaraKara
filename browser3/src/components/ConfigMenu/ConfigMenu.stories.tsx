import { ClientContext } from "@/providers/client";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { ConfigMenu } from "./ConfigMenu";

const meta = {
    title: "Components/ConfigMenu",
    component: ConfigMenu,
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
    decorators: [
        (Story) => (
            <MemoryRouter initialEntries={["/test-room"]}>
                <Routes>
                    <Route path="/:roomName" element={<Story />} />
                </Routes>
            </MemoryRouter>
        ),
    ],
} satisfies Meta<typeof ConfigMenu>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
    decorators: [
        (Story) => (
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
        ),
    ],
};

export const WithPassword: Story = {
    decorators: [
        (Story) => (
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
        ),
    ],
};

export const BoothMode: Story = {
    decorators: [
        (Story) => (
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
        ),
    ],
};

export const Fullscreen: Story = {
    decorators: [
        (Story) => (
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
        ),
    ],
};

export const AllOptionsEnabled: Story = {
    decorators: [
        (Story) => (
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
        ),
    ],
};
