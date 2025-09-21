import { useRef } from "react";

export function useMemoObj<T extends object>(obj: T): T {
    const ref = useRef<T>(obj);
    const changed = Object.keys(obj).some(
        (k) => (obj as any)[k] !== (ref.current as any)[k],
    );
    if (changed) {
        ref.current = obj;
    }
    return ref.current;
}
