import type React from "react";

import type { FAIcon } from "@shish2k/react-faicon";
import styles from "./List.module.scss";
import type { Thumb } from "./Thumb";

export function ListItem({
    thumb,
    title,
    info,
    count,
    action,
    className,
    onClick,
    ...kwargs
}: {
    thumb?: React.ReactElement<typeof Thumb>;
    title?: string | React.ReactNode;
    info?: string | React.ReactNode;
    count?: string | number;
    action?: React.ReactElement<typeof FAIcon>;
    className?: string;
    onClick?: (e: React.MouseEvent<HTMLLIElement>) => void;
    [Key: string]: any;
}): React.ReactElement {
    return (
        <li className={className} onClick={onClick} {...kwargs}>
            {thumb}
            {(title || info) && (
                <span className={styles.text}>
                    {title && <span className={styles.title}>{title}</span>}
                    {title && info && <br />}
                    {info && <span className={styles.info}>{info}</span>}
                </span>
            )}
            {count !== undefined && (
                <span className={styles.count}>{count}</span>
            )}
            {action && <span className={styles.goArrow}>{action}</span>}
        </li>
    );
}
