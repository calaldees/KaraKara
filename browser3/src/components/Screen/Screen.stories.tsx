import { ClientContext } from "@/providers/client";
import { RoomContext } from "@/providers/room";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { BrowserRouter } from "react-router-dom";
import { Screen } from "./Screen";

const meta = {
    title: "Components/Screen",
    component: Screen,
    parameters: {
        layout: "fullwidth",
    },
    tags: ["autodocs"],
    decorators: [
        (Story) => (
            <BrowserRouter>
                <ClientContext
                    value={
                        {
                            notification: null,
                            setNotification: () => {},
                            setShowSettings: () => {},
                        } as any
                    }
                >
                    <RoomContext
                        value={
                            {
                                queue: null,
                            } as any
                        }
                    >
                        <Story />
                    </RoomContext>
                </ClientContext>
            </BrowserRouter>
        ),
    ],
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

export const WithNavigation: Story = {
    args: {
        title: "Track Details",
        navLeft: <button>← Back</button>,
        navRight: <button>⋮</button>,
        children: (
            <div>
                <h2>Track Information</h2>
                <p>Details about the selected track would appear here.</p>
            </div>
        ),
    },
};

export const WithFooter: Story = {
    args: {
        title: "Queue Manager",
        footer: (
            <div
                style={{
                    display: "flex",
                    gap: "1rem",
                    justifyContent: "center",
                }}
            >
                <button>Add to Queue</button>
                <button>Clear Queue</button>
                <button>Save</button>
            </div>
        ),
        children: (
            <div>
                <p>Queue items would be listed here.</p>
                <ul>
                    <li>Track 1</li>
                    <li>Track 2</li>
                    <li>Track 3</li>
                </ul>
            </div>
        ),
    },
};

export const WithCustomClassName: Story = {
    args: {
        title: "Custom Styled Screen",
        className: "custom-screen-class",
        children: (
            <div>
                <p>This screen has a custom className applied.</p>
            </div>
        ),
    },
};

export const CompleteExample: Story = {
    args: {
        title: "Complete Screen Example",
        className: "example-screen",
        navLeft: <button>← Back to List</button>,
        navRight: <button>Settings ⚙</button>,
        footer: (
            <div style={{ display: "flex", gap: "0.5rem", padding: "1rem" }}>
                <button style={{ flex: 1 }}>Cancel</button>
                <button style={{ flex: 1 }}>Save</button>
            </div>
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

export const MinimalScreen: Story = {
    args: {
        title: "Minimal",
        children: <p>Just a title and content.</p>,
    },
};
