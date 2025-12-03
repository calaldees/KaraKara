import { faCircleChevronLeft } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { Link } from "react-router-dom";

export const BackToExplore = (): React.ReactElement => (
    <Link to={"../"} data-cy="back" aria-label="Back to Track List">
        <FAIcon icon={faCircleChevronLeft} className="x2" />
    </Link>
);
