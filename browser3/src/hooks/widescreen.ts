import { useMediaQuery } from "usehooks-ts";

/**
 * One shared media query so that different parts of the app can agree
 * on whether the screen is wide enough to show the queue and track list
 * side by side.
 */
export function useWidescreen(): boolean {
    return useMediaQuery("(min-width: 780px) and (min-aspect-ratio: 1/1)");
}
