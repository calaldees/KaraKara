import { BrowserRouter, Route, Routes } from "react-router-dom";
import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { BackToExplore } from "./BackToExplore";

const meta = {
    title: "Components/BackToExplore",
    component: BackToExplore,
    parameters: {
        layout: "centered",
    },
    tags: ["autodocs"],
    decorators: [
        (Story) => (
            <BrowserRouter>
                <Routes>
                    <Route path="*" element={<Story />} />
                </Routes>
            </BrowserRouter>
        ),
    ],
} satisfies Meta<typeof BackToExplore>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
