import { useEffect, useRef, useState } from "react";

/**
 * Hook to stabilize a boolean value that may bounce between true/false.
 * Returns true only after the value has been consistently true for a period,
 * and returns false only after the value has been problematic (flapping or
 * consistently false) for a period.
 *
 * Useful to show a "disconnected" message when a connection is flapping or
 * down, but not disturbing the user over a momentary network glitch so long
 * as it resolves itself quickly.
 *
 * @param value - The raw boolean value to stabilize (e.g., connection status)
 * @param stableDelayMs - How long value must stay true before considering it stable (default: 1000ms)
 * @param errorDelayMs - How long value must be unstable before considering it failed (default: 3000ms)
 * @returns A stabilized boolean - true if stably connected, false if connection has been bad for a while
 */
export function useStabilise(
    value: boolean,
    stableDelayMs: number = 1000,
    errorDelayMs: number = 3000,
): boolean {
    const issueStartTime = useRef<number | null>(null);
    const [isStable, setIsStable] = useState(value);

    useEffect(() => {
        // Track when issues start
        if (!value && issueStartTime.current === null) {
            // Value just went down, record when issues started
            issueStartTime.current = Date.now();
        }

        let stabilityTimer: NodeJS.Timeout | null = null;
        let errorTimer: NodeJS.Timeout | null = null;

        if (value) {
            // Value is up - wait to see if it stays stable
            stabilityTimer = setTimeout(() => {
                // Value has been stable, mark as good
                issueStartTime.current = null;
                setIsStable(true);
            }, stableDelayMs);
        } else if (issueStartTime.current !== null) {
            // Value is down - schedule error to show when delay expires
            const issuesDuration = Date.now() - issueStartTime.current;
            const remainingTime = Math.max(0, errorDelayMs - issuesDuration);
            // Use timer even for 0 delay to avoid setState during render
            errorTimer = setTimeout(() => {
                setIsStable(false);
            }, remainingTime);
        }

        return () => {
            if (stabilityTimer) clearTimeout(stabilityTimer);
            if (errorTimer) clearTimeout(errorTimer);
        };
    }, [value, stableDelayMs, errorDelayMs]);

    return isStable;
}
