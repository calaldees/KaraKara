import { useContext } from "react";

import { ClientContext } from "@/providers/client";

export function BookmarkButton({ trackId }: { trackId: string }) {
    const { bookmarks, addBookmark, removeBookmark } =
        useContext(ClientContext);

    return bookmarks.includes(trackId) ? (
        <button type="button" onClick={(_) => removeBookmark(trackId)}>
            Un-Bookmark
        </button>
    ) : (
        <button type="button" onClick={(_) => addBookmark(trackId)}>
            Bookmark
        </button>
    );
}
