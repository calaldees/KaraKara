import { faCircleChevronLeft } from "@fortawesome/free-solid-svg-icons";
import { Link } from "react-router-dom";

import { FontAwesomeIcon } from "./FontAwesomeIcon";

export const BackToExplore = (): React.ReactElement => (
    <Link to={"../"} data-cy="back">
        <FontAwesomeIcon icon={faCircleChevronLeft} className="x2" />
    </Link>
);
