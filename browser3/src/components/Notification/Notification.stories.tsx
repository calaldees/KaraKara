import { ButtonRow, Screen } from "@/components";
import { ClientContext } from "@/providers/client";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { Notification } from "./Notification";

import styles from "./Notification.module.scss";

const meta = {
    title: "Components/Notification",
    component: Notification,
    parameters: {
        kkFullscreen: true,
        layout: "padded",
    },
    tags: ["autodocs"],
} satisfies Meta<typeof Notification>;

export default meta;
type Story = StoryObj<typeof meta>;

const testStyles = {
    position: "relative",
    marginBottom: "1rem",
    width: "20em",
} as React.CSSProperties;

export const ColourTest: Story = {
    decorators: [
        () => (
            <Screen
                title="Notifications"
                footer={
                    <ButtonRow>
                        <button>Test Button 1</button>
                        <button>Test Button 2</button>
                    </ButtonRow>
                }
            >
                <div style={testStyles} className={`${styles.notification} ok`}>
                    OK Notification
                </div>
                <div
                    style={testStyles}
                    className={`${styles.notification} warning`}
                >
                    Warning Notification
                </div>
                <div
                    style={testStyles}
                    className={`${styles.notification} error`}
                >
                    Error Notification
                </div>
            </Screen>
        ),
    ],
};

export const Ok: Story = {
    decorators: [
        (Story) => (
            <ClientContext
                value={
                    {
                        notification: {
                            text: "Operation completed successfully!",
                            style: "ok",
                        },
                        setNotification: () => {},
                    } as any
                }
            >
                <Story />
            </ClientContext>
        ),
    ],
};

export const Warning: Story = {
    decorators: [
        (Story) => (
            <ClientContext
                value={
                    {
                        notification: {
                            text: "Warning: Your session is about to expire",
                            style: "warning",
                        },
                        setNotification: () => {},
                    } as any
                }
            >
                <Story />
            </ClientContext>
        ),
    ],
};

export const Error: Story = {
    decorators: [
        (Story) => (
            <ClientContext
                value={
                    {
                        notification: {
                            text: "An error occurred. Please try again.",
                            style: "error",
                        },
                        setNotification: () => {},
                    } as any
                }
            >
                <Story />
            </ClientContext>
        ),
    ],
};

export const NoNotification: Story = {
    decorators: [
        (Story) => (
            <ClientContext
                value={
                    {
                        notification: null,
                        setNotification: () => {},
                    } as any
                }
            >
                <Story />
            </ClientContext>
        ),
    ],
};

export const LongMessage: Story = {
    decorators: [
        (Story) => (
            <ClientContext
                value={
                    {
                        notification: {
                            text: "This is a very long notification message that contains a lot of information and might wrap to multiple lines depending on the screen size.",
                            style: "ok",
                        },
                        setNotification: () => {},
                    } as any
                }
            >
                <Story />
            </ClientContext>
        ),
    ],
};
