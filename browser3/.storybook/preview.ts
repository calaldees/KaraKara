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
    },
    decorators: [withTestHarness],
};

export default preview;
