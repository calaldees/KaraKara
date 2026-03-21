import { faCircleChevronLeft } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { Link, useParams } from "react-router-dom";

export function BackToExplore(): React.ReactElement {
    const { roomName } = useParams();
    return (
        <Link
            to={`/${roomName}`}
            data-cy="back"
            aria-label="Back to Track List"
            role="button"
        >
            <FAIcon icon={faCircleChevronLeft} />
        </Link>
    );
}
