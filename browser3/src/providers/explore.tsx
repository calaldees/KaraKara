import { createContext, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useMemoObj } from "../hooks/memo";

interface ExploreContextType {
    search: string;
    setSearch: (_: string) => void;
    filters: string[];
    setFilters: (_: any) => void;
    expanded: string | null;
    setExpanded: (_: string | null) => void;
}

/* eslint-disable react-refresh/only-export-components */
export const ExploreContext = createContext<ExploreContextType>(
    {} as ExploreContextType,
);

export function ExploreProvider(props: any) {
    const [expanded, setExpanded] = useState<string | null>(null);
    const [inSearch, setInSearch] = useState(false);

    const [searchParams, setSearchParams] = useSearchParams();
    const search = searchParams.get("search") ?? "";
    const filters = searchParams.getAll("filters");

    function setSearch(new_search: string | ((search: string) => string)) {
        const updatedSearch =
            typeof new_search === "function" ? new_search(search) : new_search;
        setSearchParams(
            { search: updatedSearch, filters },
            { replace: inSearch },
        );
        setInSearch(true);
    }

    function setFilters(
        new_filters: string[] | ((filters: string[]) => string[]),
    ) {
        const updatedFilters =
            typeof new_filters === "function"
                ? new_filters(filters)
                : new_filters;
        setSearchParams({ search, filters: updatedFilters });
        setInSearch(false);
    }

    const ctxVal = useMemoObj({
        search,
        setSearch,
        filters,
        setFilters,
        expanded,
        setExpanded,
    });
    return <ExploreContext value={ctxVal}>{props.children}</ExploreContext>;
}
