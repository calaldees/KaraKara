import { createContext, useEffect, useState } from "react";
import type { NavigateFunction } from "react-router-dom";
import { useLocation, useNavigate, useParams } from "react-router-dom";

export interface PageContextType {
    roomName: string | undefined;
    hasBack: boolean;
    navigate: NavigateFunction;
}

/* eslint-disable react-refresh/only-export-components */
export const PageContext = createContext<PageContextType>(
    {} as PageContextType,
);

export function PageProvider(props: any) {
    const { roomName } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const [internalNavigationCounter, setInternalNavigationCounter] =
        useState(0);

    // Intentionally tracking navigation changes to determine if back button should be available
    // This setState in useEffect is by design - we want to increment on every location change
    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setInternalNavigationCounter((prev) => prev + 1);
    }, [location]);

    const hasBack = internalNavigationCounter > 1;

    return (
        <PageContext value={{ roomName, hasBack, navigate }}>
            {props.children}
        </PageContext>
    );
}
