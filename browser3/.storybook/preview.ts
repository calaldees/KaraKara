import type { Preview } from "storybook-react-rsbuild";
import "../src/static/forms.scss";
import "../src/static/layout.scss";
import "../src/static/vars.scss";

const preview: Preview = {
    parameters: {
        controls: {
            matchers: {
                color: /(background|color)$/i,
                date: /Date$/i,
            },
        },
    },
};

export default preview;
