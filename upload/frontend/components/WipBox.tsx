import { useEffect, useState } from "react";

interface Wip {
    title: string;
    artist?: string;
    from?: string;
    status?: string;
}

export const WipBox = () => {
    const [wips, setWips] = useState<Wip[] | null>(null);

    useEffect(() => {
        fetch("./wips")
            .then((res) => res.json())
            .then((data) => {
                if (Array.isArray(data.wips)) {
                    setWips(data.wips);
                }
            })
            .catch((err) => {
                console.log(err);
                setWips([{ title: "Failed to load work-in-progress tracks" }]);
            });
    }, []);

    return (
        <section className="wip-box">
            <h3>Work-in-Progress Tracks</h3>
            <ul id="wips">
                {wips === null ? (
                    <li>Loading...</li>
                ) : wips.length === 0 ? (
                    <li>The queue is empty /o/</li>
                ) : (
                    wips.map((wip, idx) => (
                        <li key={idx}>
                            <strong>{wip.title}</strong>
                            {wip.artist && (
                                <>
                                    {" "}
                                    &mdash; <span>{wip.artist}</span>
                                </>
                            )}
                            {wip.from && (
                                <>
                                    {" "}
                                    (<span>{wip.from}</span>)
                                </>
                            )}
                            {wip.status && (
                                <>
                                    {" "}
                                    &mdash; <em>{wip.status}</em>
                                </>
                            )}
                        </li>
                    ))
                )}
            </ul>
        </section>
    );
};
