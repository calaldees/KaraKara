import type { Preview } from "storybook-react-rsbuild";
import "../src/static/forms.scss";
import "../src/static/layout.scss";
import "../src/static/vars.scss";
import { withTestHarness } from "./decorators";

const preview: Preview = {
    parameters: {
        controls: {
            matchers: {
                color: /(background|color)$/i,
                date: /Date$/i,
            },
        },
        kkFullscreen: false,
    },
    decorators: [
        withTestHarness,
        (Story, { parameters }) => {
            if (parameters.kkFullscreen)
                return (
                    <div id="page">
                        <Story />
                    </div>
                );
            return <Story />;
        },
    ],
};

export default preview;
