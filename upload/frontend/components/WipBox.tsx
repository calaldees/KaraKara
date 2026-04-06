import { useEffect, useState } from "react";

interface Wip {
    id: string;
    title: string;
    artist?: string;
    from?: string;
    status?: string;
}

export const WipBox = () => {
    const [wips, setWips] = useState<Wip[] | null>(null);

    useEffect(() => {
        fetch("/api/upload/wips")
            .then((res) => res.json())
            .then((data) => {
                if (Array.isArray(data.wips)) {
                    setWips(data.wips);
                }
            })
            .catch((err) => {
                console.log(err);
                setWips([
                    { id: "", title: "Failed to load work-in-progress tracks" },
                ]);
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
                    wips
                        .sort((a, b) => a.title.localeCompare(b.title))
                        .map((wip) => (
                            <li key={wip.id}>
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
                                    <ul>
                                        <li>
                                            <em>{wip.status}</em>
                                        </li>
                                    </ul>
                                )}
                            </li>
                        ))
                )}
            </ul>
        </section>
    );
};
