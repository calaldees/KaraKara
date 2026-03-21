import styles from "./ButtonRow.module.scss";

export function ButtonRow({
    children,
}: {
    children: React.ReactNode;
}): React.ReactElement {
    return <div className={styles.buttonRow}>{children}</div>;
}
