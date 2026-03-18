import type React from "react";

import styles from "./List.module.scss";

export function List({
    children,
    onDragLeave,
}: {
    children: React.ReactNode;
    onDragLeave?: (e: React.DragEvent<HTMLUListElement>) => void;
}): React.ReactElement {
    return (
        <ul className={styles.list} onDragLeave={onDragLeave}>
            {children}
        </ul>
    );
}
