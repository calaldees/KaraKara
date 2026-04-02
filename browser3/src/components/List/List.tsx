import type React from "react";

import styles from "./List.module.scss";

export function List({
    children,
    onDragLeave,
    twoColumn = false,
}: {
    children: React.ReactNode;
    onDragLeave?: (e: React.DragEvent<HTMLUListElement>) => void;
    twoColumn?: boolean;
}): React.ReactElement {
    return (
        <ul 
            className={`${styles.list} ${twoColumn ? styles.twoColumn : ''}`} 
            onDragLeave={onDragLeave}
        >
            {children}
        </ul>
    );
}
