import { faPlus, faTrash } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useState } from "react";

import styles from "./TagsEditor.module.scss";

// Tags that should use checkbox editors with values from the database
const CHECKBOX_TAG_KEYS = [
    "category",
    "use",
    "vocaltrack",
    "vocalstyle",
    "lang",
];

// Tags that should use date picker editors
const DATE_TAG_KEYS = ["released", "date", "added", "updated"];

interface TextInputEditorProps {
    values: string[];
    onChange: (values: string[]) => void;
}

function TextInputEditor({ values, onChange }: TextInputEditorProps) {
    const handleChange = (index: number, newValue: string) => {
        const newValues = [...values];
        newValues[index] = newValue;
        onChange(newValues);
    };

    const handleAdd = () => {
        onChange([...values, ""]);
    };

    const handleRemove = (index: number) => {
        onChange(values.filter((_, i) => i !== index));
    };

    return (
        <div className={styles.textInputEditor}>
            {values.map((value, index) => (
                <div key={index} className={styles.textInputRow}>
                    <input
                        type="text"
                        value={value}
                        onChange={(e) => handleChange(index, e.target.value)}
                        className={styles.textInput}
                    />
                    <FAIcon
                        icon={faTrash}
                        className={styles.removeIcon}
                        onClick={() => handleRemove(index)}
                        role="button"
                        aria-label="Remove value"
                    />
                </div>
            ))}
            <button
                type="button"
                onClick={handleAdd}
                className={styles.addValueButton}
            >
                <FAIcon icon={faPlus} /> Add value
            </button>
        </div>
    );
}

interface CheckboxEditorProps {
    values: string[];
    possibleValues: string[];
    onChange: (values: string[]) => void;
}

function CheckboxEditor({
    values,
    possibleValues,
    onChange,
}: CheckboxEditorProps) {
    const handleToggle = (value: string) => {
        if (values.includes(value)) {
            onChange(values.filter((v) => v !== value));
        } else {
            onChange([...values, value]);
        }
    };

    return (
        <div className={styles.checkboxEditor}>
            {possibleValues.map((possibleValue) => (
                <label key={possibleValue} className={styles.checkboxLabel}>
                    <input
                        type="checkbox"
                        checked={values.includes(possibleValue)}
                        onChange={() => handleToggle(possibleValue)}
                        className={styles.checkbox}
                    />
                    {possibleValue}
                </label>
            ))}
        </div>
    );
}

interface DateEditorProps {
    values: string[];
    onChange: (values: string[]) => void;
}

function DateEditor({ values, onChange }: DateEditorProps) {
    const dateValue = values[0] || "";

    const handleChange = (newValue: string) => {
        onChange(newValue ? [newValue] : []);
    };

    return (
        <div className={styles.dateEditor}>
            <input
                type="date"
                value={dateValue}
                onChange={(e) => handleChange(e.target.value)}
                className={styles.dateInput}
            />
        </div>
    );
}

interface TagRowProps {
    tagKey: string;
    values: string[];
    possibleValues: string[];
    onSave: (newValues: string[]) => void;
}

function TagRow({ tagKey, values, possibleValues, onSave }: TagRowProps) {
    const [localValues, setLocalValues] = useState<string[]>(values);
    const [isDirty, setIsDirty] = useState(false);

    const handleChange = (newValues: string[]) => {
        setLocalValues(newValues);
        setIsDirty(true);
    };

    const handleSave = () => {
        onSave(localValues);
        setIsDirty(false);
    };

    const handleCancel = () => {
        setLocalValues(values);
        setIsDirty(false);
    };

    const renderEditor = () => {
        if (DATE_TAG_KEYS.includes(tagKey)) {
            return <DateEditor values={localValues} onChange={handleChange} />;
        } else if (CHECKBOX_TAG_KEYS.includes(tagKey)) {
            return (
                <CheckboxEditor
                    values={localValues}
                    possibleValues={possibleValues}
                    onChange={handleChange}
                />
            );
        } else {
            // Default to text input editor for MULTI_TEXT_TAG_KEYS and unknown keys
            return (
                <TextInputEditor values={localValues} onChange={handleChange} />
            );
        }
    };

    return (
        <div className={styles.tagRow}>
            <div className={styles.tagKey}>{tagKey}</div>
            <div className={styles.tagEditor}>
                {renderEditor()}
                {isDirty && (
                    <div className={styles.tagActions}>
                        <button
                            type="button"
                            onClick={handleSave}
                            className={styles.saveButton}
                        >
                            Save
                        </button>
                        <button
                            type="button"
                            onClick={handleCancel}
                            className={styles.cancelButton}
                        >
                            Cancel
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export function TagsEditor({
    tags,
    possibleValuesByKey,
    onChanged,
}: {
    tags: Record<string, string[]>;
    possibleValuesByKey: Record<string, string[]>;
    onChanged: (tagKey: string, newValues: string[]) => void;
}) {
    const editableTags = Object.keys(tags)
        .filter((key) => !key.startsWith("_"))
        .sort();

    return (
        <div className={styles.tagsEditor}>
            {editableTags.map((tagKey) => (
                <TagRow
                    key={tagKey}
                    tagKey={tagKey}
                    values={tags[tagKey] || []}
                    possibleValues={possibleValuesByKey[tagKey] || []}
                    onSave={(newValues) => onChanged(tagKey, newValues)}
                />
            ))}
        </div>
    );
}
