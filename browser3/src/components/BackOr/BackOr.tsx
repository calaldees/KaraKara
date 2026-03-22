import { faCircleChevronLeft } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext } from "react";

import { PageContext } from "@/providers/page";

export function BackOr({ to }: { to: string }): React.ReactElement {
    const { hasBack, navigate } = useContext(PageContext);

    const handleClick = () => {
        if (hasBack) {
            void navigate(-1);
        } else {
            void navigate(to);
        }
    };

    return (
        <FAIcon
            icon={faCircleChevronLeft}
            onClick={handleClick}
            data-cy="back"
            aria-label="Back"
        />
    );
}
