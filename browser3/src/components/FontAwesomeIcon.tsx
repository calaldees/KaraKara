// This is a minimal reimplementation of FontAwesomeIcon
// to avoid pulling in the whole ~80kb library
// See https://docs.fontawesome.com/v5/web/use-with/react

export function FontAwesomeIcon({
    icon,
    className = "",
}: {
    icon: any;
    className?: string;
}) {
    const [width, height, _aliases, _unicode, svgPathData] = icon.icon;
    return (
        <svg
            aria-hidden="true"
            focusable="false"
            data-prefix={icon.prefix}
            data-icon={icon.iconName}
            className={`svg-inline--fa fa-${icon.iconName} ${className}`}
            role="img"
            xmlns="http://www.w3.org/2000/svg"
            viewBox={`0 0 ${width} ${height}`}
        >
            <path fill="currentColor" d={svgPathData}></path>
        </svg>
    );
}
