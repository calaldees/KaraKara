import { useCallback, useEffect, useState } from "react";

export function useCookieStore<T extends string | null>(
    name: string,
    initialValue: T,
): [T, (value: T, options?: object) => void, () => void] {
    const [value, setValue] = useState<T>(initialValue);

    // load initial value (done as a separate useEffect
    // because useState initializer cannot be async)
    useEffect(() => {
        cookieStore
            .get(name)
            .then((cookie) => {
                if (cookie && cookie.value) setValue(cookie.value as T);
            })
            .catch((e) => console.error(e));
    }, [name]);

    const updateCookie = useCallback(
        (newValue: T, options: object = {}) => {
            if (newValue)
                cookieStore
                    .set({ name, value: newValue, ...options })
                    .then(() => setValue(newValue))
                    .catch((e) => console.error(e));
        },
        [name],
    );

    useEffect(() => {
        function cookieListener(e: CookieChangeEvent): void {
            const changedCookie = e.changed.find((c) => c.name === name);
            if (changedCookie && changedCookie.value) {
                setValue(changedCookie.value as T);
            }

            const deletedCookie = e.deleted.find((c) => c.name === name);
            if (deletedCookie) {
                setValue(initialValue);
            }
        }
        cookieStore.addEventListener("change", cookieListener);

        return () => cookieStore.removeEventListener("change", cookieListener);
    });

    const deleteCookie = useCallback(() => {
        cookieStore
            .delete(name)
            .then(() => setValue(initialValue))
            .catch((e) => console.error(e));
    }, [name, initialValue]);

    return [value, updateCookie, deleteCookie];
}
