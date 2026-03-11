import { InfoBox } from "../components/InfoBox";
import { UploadForm } from "../components/UploadForm";
import { WipBox } from "../components/WipBox";

export function Index() {
    return (
        <main>
            <h1>KaraKara Track Submission</h1>

            <div className="columns">
                <div id="info" className="column">
                    <InfoBox />
                    <WipBox />
                </div>

                <div className="column">
                    <UploadForm />
                </div>
            </div>
        </main>
    );
}
