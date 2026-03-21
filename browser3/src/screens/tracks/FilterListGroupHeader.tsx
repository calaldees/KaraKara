import { faCircleMinus, faCirclePlus } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext } from "react";

import { ListItem } from "@/components";
import { ExploreContext } from "@/providers/explore";

export function FilterListGroupHeader({
    filter,
    count,
    expanded,
    children,
}: {
    filter: string;
    count: number;
    expanded: boolean;
    children: React.ReactNode;
}): React.ReactElement {
    const { setExpanded } = useContext(ExploreContext);

    return (
        <ListItem
            title={children}
            count={count}
            action={<FAIcon icon={expanded ? faCircleMinus : faCirclePlus} />}
            onClick={(_) => setExpanded(expanded ? null : filter)}
        />
    );
}
