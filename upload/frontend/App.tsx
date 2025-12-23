import "./App.css";
import { InfoBox } from "./components/InfoBox";
import { WipBox } from "./components/WipBox";
import { UploadForm } from "./components/UploadForm";

const App = () => {
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
};

export default App;
