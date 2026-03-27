import {
    faArrowDown,
    faArrowUp,
    faPlus,
    faTrash,
} from "@fortawesome/free-solid-svg-icons";
import Form from "@rjsf/core";
import type { IconButtonProps, RJSFSchema } from "@rjsf/utils";
import validator from "@rjsf/validator-ajv8";
import { FAIcon } from "@shish2k/react-faicon";
import { useCallback, useContext } from "react";

import { BackOr, ButtonRow, Screen } from "@/components";
import { useApi } from "@/hooks/api";
import { PageContext } from "@/providers/page";
import { RoomContext } from "@/providers/room";
import { SettingsSchema } from "@/schemas";
import type { Settings } from "@/types";

import "./settings.scss";

// Custom IconButton component using FAIcon
function IconButton(
    props: IconButtonProps & { icon: string },
): React.ReactElement {
    const { icon, iconType: _iconType, ...otherProps } = props;
    const iconMap: Record<string, any> = {
        plus: faPlus,
        "arrow-up": faArrowUp,
        "arrow-down": faArrowDown,
        remove: faTrash,
    };

    const faIcon = iconMap[icon] || faPlus;

    return (
        <button type="button" {...otherProps}>
            <FAIcon icon={faIcon} />
        </button>
    );
}

// Custom templates to use FAIcon
const templates = {
    ButtonTemplates: {
        AddButton: (props: any) => <IconButton {...props} icon="plus" />,
        MoveUpButton: (props: any) => <IconButton {...props} icon="arrow-up" />,
        MoveDownButton: (props: any) => (
            <IconButton {...props} icon="arrow-down" />
        ),
        RemoveButton: (props: any) => <IconButton {...props} icon="remove" />,
    },
};

// UI Schema to customize the form rendering
const uiSchema = {
    "ui:submitButtonOptions": {
        norender: true,
    },
    preview_volume: {
        "ui:widget": "range",
    },
    hidden_tags: {
        "ui:options": {
            orderable: false,
        },
    },
    forced_tags: {
        "ui:options": {
            orderable: false,
        },
    },
};

function RoomSettings(): React.ReactElement {
    const { roomName } = useContext(PageContext);
    const { settings: roomSettings } = useContext(RoomContext);
    const { request, loading } = useApi();

    const saveSettings = useCallback(
        (data: { formData?: Settings }) => {
            if (!data.formData) return;

            request({
                notify: "Saving settings...",
                notify_ok: "Settings saved!",
                function: "settings",
                options: {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(data.formData),
                },
            });
        },
        [request],
    );

    const buttons = (
        <ButtonRow>
            <button
                type="submit"
                form="settings-form"
                data-cy="save-settings-button"
                disabled={loading}
            >
                Save
            </button>
        </ButtonRow>
    );

    return (
        <Screen
            className={"settings"}
            navLeft={<BackOr to={`/${roomName}`} />}
            title={"Room Settings"}
            footer={buttons}
        >
            <Form
                id="settings-form"
                schema={SettingsSchema as unknown as RJSFSchema}
                uiSchema={uiSchema}
                formData={roomSettings}
                // @ts-expect-error - Complex generic type incompatibility with RJSF
                validator={validator}
                templates={templates}
                onSubmit={saveSettings}
                disabled={loading}
                showErrorList={false}
                liveValidate={true}
            />
        </Screen>
    );
}

export default RoomSettings;
