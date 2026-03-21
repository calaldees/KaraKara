import { useContext } from "react";

import { List } from "@/components";
import { ExploreContext } from "@/providers/explore";
import { normalise_cmp } from "@/utils";

import { FilterList } from "./FilterList";
import { FilterListGroupHeader } from "./FilterListGroupHeader";

import styles from "./GroupedFilterList.module.scss";

export function GroupedFilterList({
    heading,
    filters,
}: {
    heading: string;
    filters: Record<string, Record<string, number>>;
}): React.ReactElement {
    const { expanded } = useContext(ExploreContext);

    return (
        <List>
            {Object.keys(filters)
                .sort(normalise_cmp)
                .map((group) =>
                    group === expanded ? (
                        <div key={group} className={styles.filterListGroup}>
                            <FilterListGroupHeader
                                filter={group}
                                count={Object.keys(filters[group]).length}
                                expanded={true}
                            >
                                {group}
                            </FilterListGroupHeader>
                            <FilterList
                                heading={heading}
                                filters={filters[group]}
                            />
                        </div>
                    ) : (
                        <FilterListGroupHeader
                            key={group}
                            filter={group}
                            count={Object.keys(filters[group]).length}
                            expanded={false}
                        >
                            {group}
                        </FilterListGroupHeader>
                    ),
                )}
        </List>
    );
}
