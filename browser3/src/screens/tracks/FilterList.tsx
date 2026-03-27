import { faCircleChevronRight } from "@fortawesome/free-solid-svg-icons";
import { FAIcon } from "@shish2k/react-faicon";
import { useContext } from "react";

import { List, ListItem } from "@/components";
import { ExploreContext } from "@/providers/explore";
import { normalise_cmp } from "@/utils";

import styles from "./FilterList.module.scss";

function unThe(filter: string): string {
    if (filter.toLowerCase().endsWith(", the")) {
        return (
            filter.substring(filter.length - 3) +
            " " +
            filter.substring(0, filter.length - 5)
        );
    }
    return filter;
}

export function FilterList({
    heading,
    filters,
}: {
    heading: string;
    filters: Record<string, number>;
}): React.ReactElement {
    const { setFilters, setExpanded } = useContext(ExploreContext);

    return (
        <List>
            {Object.keys(filters)
                .sort(normalise_cmp)
                .map((child) => (
                    <ListItem
                        key={child}
                        className={styles.addFilter}
                        title={child}
                        count={filters[child]}
                        action={<FAIcon icon={faCircleChevronRight} />}
                        onClick={(_) => {
                            setExpanded(null);
                            setFilters((fs: string[]) => [
                                ...fs,
                                `${heading}:${unThe(child)}`,
                            ]);
                        }}
                    />
                ))}
        </List>
    );
}
