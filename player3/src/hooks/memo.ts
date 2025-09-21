import { useMemo } from "react";

export function useMemoObj<T extends object>(obj: T): T {
    // eslint-disable-next-line react-hooks/exhaustive-deps
    return useMemo<T>(() => obj, Object.values(obj));
}

export const useMemoArr = useMemo;
