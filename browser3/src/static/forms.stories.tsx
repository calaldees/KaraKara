import type { Meta, StoryObj } from "storybook-react-rsbuild";
import { ButtonRow, Screen } from "@/components";

// Shared container style
const Container = ({ children }: { children: React.ReactNode }) => (
    <div
        style={{
            padding: "2rem",
            width: "100%",
            maxWidth: "800px",
            margin: "0 auto",
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
        }}
    >
        {children}
    </div>
);

// Text Inputs Component
const TextInputs = () => (
    <Container>
        <div>
            <label htmlFor="text-input">Text Input</label>
            <input id="text-input" type="text" placeholder="Enter text..." />
        </div>

        <div>
            <label htmlFor="text-input-value">Text Input (with value)</label>
            <input
                id="text-input-value"
                type="text"
                value="Sample text"
                readOnly
            />
        </div>

        <div>
            <label htmlFor="text-input-disabled">Text Input (disabled)</label>
            <input
                id="text-input-disabled"
                type="text"
                placeholder="Disabled Placeholder"
                disabled
            />
        </div>

        <div>
            <label htmlFor="text-input-disabled">
                Text Input (disabled with value)
            </label>
            <input
                id="text-input-disabled"
                type="text"
                placeholder="Disabled"
                value="Disabled Value"
                disabled
            />
        </div>

        <div>
            <label htmlFor="email-input">Email Input</label>
            <input
                id="email-input"
                type="email"
                placeholder="email@example.com"
            />
        </div>

        <div>
            <label htmlFor="password-input">Password Input</label>
            <input id="password-input" type="password" placeholder="Password" />
        </div>

        <div>
            <label htmlFor="tel-input">Tel Input</label>
            <input id="tel-input" type="tel" placeholder="123-456-7890" />
        </div>

        <div>
            <label htmlFor="url-input">URL Input</label>
            <input
                id="url-input"
                type="url"
                placeholder="https://example.com"
            />
        </div>

        <div>
            <label htmlFor="search-input">Search Input</label>
            <input id="search-input" type="search" placeholder="Search..." />
        </div>
    </Container>
);

// Number & Range Inputs Component
const NumberRangeInputs = () => (
    <Container>
        <div>
            <label htmlFor="number-input">Number Input</label>
            <input
                id="number-input"
                type="number"
                placeholder="42"
                min="0"
                max="100"
            />
        </div>

        <div>
            <label htmlFor="range-input">Range Input (0-100)</label>
            <input
                id="range-input"
                type="range"
                min="0"
                max="100"
                defaultValue="50"
            />
        </div>
    </Container>
);

// Date & Time Inputs Component
const DateTimeInputs = () => (
    <Container>
        <div>
            <label htmlFor="date-input">Date Input</label>
            <input id="date-input" type="date" />
        </div>

        <div>
            <label htmlFor="datetime-local-input">DateTime-Local Input</label>
            <input id="datetime-local-input" type="datetime-local" />
        </div>

        <div>
            <label htmlFor="time-input">Time Input</label>
            <input id="time-input" type="time" />
        </div>

        <div>
            <label htmlFor="month-input">Month Input</label>
            <input id="month-input" type="month" />
        </div>

        <div>
            <label htmlFor="week-input">Week Input</label>
            <input id="week-input" type="week" />
        </div>
    </Container>
);

// Color & File Inputs Component
const ColorFileInputs = () => (
    <Container>
        <div>
            <label htmlFor="color-input">Color Input</label>
            <input id="color-input" type="color" defaultValue="#ff0000" />
        </div>

        <div>
            <label htmlFor="file-input">File Input</label>
            <input id="file-input" type="file" />
        </div>

        <div>
            <label htmlFor="file-multiple-input">File Input (multiple)</label>
            <input id="file-multiple-input" type="file" multiple />
        </div>
    </Container>
);

// Checkboxes & Radio Buttons Component
const CheckboxesRadios = () => (
    <Container>
        <div>
            <label>
                <input type="checkbox" />
                Checkbox unchecked
            </label>
        </div>

        <div>
            <label>
                <input type="checkbox" defaultChecked />
                Checkbox checked
            </label>
        </div>

        <div>
            <label>
                <input type="checkbox" disabled />
                Checkbox disabled
            </label>
        </div>

        <div>
            <label>
                <input type="checkbox" defaultChecked disabled />
                Checkbox checked & disabled
            </label>
        </div>

        <fieldset>
            <legend>Radio Group</legend>
            <div
                style={{
                    display: "flex",
                    flexDirection: "column",
                    gap: "0.5rem",
                }}
            >
                <label>
                    <input
                        type="radio"
                        name="radio-group"
                        value="option1"
                        defaultChecked
                    />
                    Option 1
                </label>
                <label>
                    <input type="radio" name="radio-group" value="option2" />
                    Option 2
                </label>
                <label>
                    <input type="radio" name="radio-group" value="option3" />
                    Option 3
                </label>
                <label>
                    <input
                        type="radio"
                        name="radio-group"
                        value="option4"
                        disabled
                    />
                    Option 4 (disabled)
                </label>
            </div>
        </fieldset>
    </Container>
);

// Select Dropdowns Component
const Selects = () => (
    <Container>
        <div>
            <label htmlFor="select-single">Single Select</label>
            <select id="select-single">
                <option value="">-- Choose an option --</option>
                <option value="1">Option 1</option>
                <option value="2">Option 2</option>
                <option value="3">Option 3</option>
            </select>
        </div>

        <div>
            <label htmlFor="select-grouped">Select with Groups</label>
            <select id="select-grouped">
                <option value="">-- Choose an option --</option>
                <optgroup label="Group 1">
                    <option value="1a">Option 1A</option>
                    <option value="1b">Option 1B</option>
                </optgroup>
                <optgroup label="Group 2">
                    <option value="2a">Option 2A</option>
                    <option value="2b">Option 2B</option>
                </optgroup>
            </select>
        </div>

        <div>
            <label htmlFor="select-multiple">Multiple Select</label>
            <select id="select-multiple" multiple size={4}>
                <option value="1">Option 1</option>
                <option value="2">Option 2</option>
                <option value="3">Option 3</option>
                <option value="4">Option 4</option>
            </select>
        </div>

        <div>
            <label htmlFor="select-disabled">Select (disabled)</label>
            <select id="select-disabled" disabled>
                <option value="">Disabled select</option>
            </select>
        </div>
    </Container>
);

// Textareas Component
const Textareas = () => (
    <Container>
        <div>
            <label htmlFor="textarea">Textarea</label>
            <textarea
                id="textarea"
                rows={4}
                placeholder="Enter multiple lines of text..."
            />
        </div>

        <div>
            <label htmlFor="textarea-value">Textarea (with value)</label>
            <textarea
                id="textarea-value"
                rows={4}
                defaultValue="This is some sample text.&#10;It has multiple lines.&#10;Line 3 here."
            />
        </div>

        <div>
            <label htmlFor="textarea-disabled">Textarea (disabled)</label>
            <textarea
                id="textarea-disabled"
                rows={4}
                placeholder="Disabled textarea"
                disabled
            />
        </div>
    </Container>
);

// Buttons Component
const Buttons = () => (
    <Container>
        <button type="button">Button</button>
        <button type="submit">Submit Button</button>
        <button type="reset">Reset Button</button>
        <button type="button" disabled>
            Disabled Button
        </button>

        <input type="button" value="Input Button" />
        <input type="submit" value="Input Submit" />
        <input type="reset" value="Input Reset" />
        <input type="button" value="Input Disabled" disabled />

        <a href="#" className="button">
            Link styled as button
        </a>
    </Container>
);

// Other Elements Component
const OtherElements = () => (
    <Container>
        <div>
            <label htmlFor="datalist-input">Input with Datalist</label>
            <input
                id="datalist-input"
                type="text"
                list="suggestions"
                placeholder="Type to see suggestions..."
            />
            <datalist id="suggestions">
                <option value="Aardvark" />
                <option value="Alice" />
                <option value="Longer Word" />
                <option value="Longlonglong" />
            </datalist>
        </div>

        <fieldset>
            <legend>Fieldset with Legend</legend>
            <label htmlFor="inside-fieldset">Input inside fieldset</label>
            <input id="inside-fieldset" type="text" placeholder="Text input" />
        </fieldset>

        <div>
            <label htmlFor="progress-bar">Progress Bar</label>
            <progress id="progress-bar" value="70" max="100">
                70%
            </progress>
        </div>

        <div>
            <label htmlFor="meter-bar">Meter</label>
            <meter
                id="meter-bar"
                min="0"
                max="100"
                low={30}
                high={70}
                optimum={80}
                value="50"
            >
                50
            </meter>
        </div>

        <div>
            <label htmlFor="output">Output Element</label>
            <output id="output" name="result" htmlFor="number-input">
                Result: 42
            </output>
        </div>
    </Container>
);

// Complete Form Example Component
const CompleteForm = () => (
    <Container>
        <form
            style={{
                display: "flex",
                flexDirection: "column",
                gap: "1rem",
            }}
        >
            <div>
                <label htmlFor="form-name">Name</label>
                <input
                    id="form-name"
                    type="text"
                    placeholder="Your name"
                    required
                />
            </div>

            <div>
                <label htmlFor="form-email">Email</label>
                <input
                    id="form-email"
                    type="email"
                    placeholder="your@email.com"
                    required
                />
            </div>

            <div>
                <label htmlFor="form-category">Category</label>
                <select id="form-category">
                    <option value="">Select...</option>
                    <option value="feedback">Feedback</option>
                    <option value="bug">Bug Report</option>
                    <option value="feature">Feature Request</option>
                </select>
            </div>

            <div>
                <label htmlFor="form-message">Message</label>
                <textarea
                    id="form-message"
                    rows={4}
                    placeholder="Your message..."
                    required
                />
            </div>

            <div>
                <label>
                    <input type="checkbox" required />I agree to the terms
                </label>
            </div>

            <ButtonRow>
                <button type="submit">Submit</button>
                <button type="reset">Reset</button>
            </ButtonRow>
        </form>
    </Container>
);

// All Form Elements Combined
const AllFormElements = () => (
    <div
        style={{
            display: "flex",
            flexDirection: "column",
            gap: "1rem",
        }}
    >
        <Container>
            <p>
                A comprehensive showcase of all HTML form elements with current
                styling.
            </p>
        </Container>
        <TextInputs />
        <NumberRangeInputs />
        <DateTimeInputs />
        <ColorFileInputs />
        <CheckboxesRadios />
        <Selects />
        <Textareas />
        <Buttons />
        <OtherElements />
        <CompleteForm />
    </div>
);

// Meta configuration
const meta: Meta = {
    title: "Static/Forms",
    parameters: {
        kkFullscreen: true,
        layout: "fullscreen",
    },
    decorators: [
        (Story) => (
            <Screen
                title="Test"
                footer={
                    <>
                        <input type="text" placeholder="Footer input" />
                        <ButtonRow>
                            <button>Double-Submit</button>
                            <button>Double-Reset</button>
                        </ButtonRow>
                    </>
                }
            >
                <Story />
            </Screen>
        ),
    ],
};

export default meta;

// Stories
export const Form: StoryObj = {
    name: "Complete Form",
    render: () => <CompleteForm />,
};

export const All: StoryObj = {
    render: () => <AllFormElements />,
};

export const TextInputsStory: StoryObj = {
    name: "Text Inputs",
    render: () => <TextInputs />,
};

export const NumberAndRange: StoryObj = {
    name: "Number & Range",
    render: () => <NumberRangeInputs />,
};

export const DateAndTime: StoryObj = {
    name: "Date & Time",
    render: () => <DateTimeInputs />,
};

export const ColorAndFile: StoryObj = {
    name: "Color & File",
    render: () => <ColorFileInputs />,
};

export const CheckboxesAndRadios: StoryObj = {
    name: "Checkboxes & Radios",
    render: () => <CheckboxesRadios />,
};

export const SelectDropdowns: StoryObj = {
    name: "Select Dropdowns",
    render: () => <Selects />,
};

export const TextareasStory: StoryObj = {
    name: "Textareas",
    render: () => <Textareas />,
};

export const ButtonsStory: StoryObj = {
    name: "Buttons",
    render: () => <Buttons />,
};

export const Other: StoryObj = {
    name: "Other Elements",
    render: () => <OtherElements />,
};
