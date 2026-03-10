import { BrowserRouter, Route, Routes } from "react-router-dom";
import "./App.css";
import { Index } from "./screens/index";

const App = () => {
    return (
        <BrowserRouter basename={import.meta.env.BASE_URL}>
            <Routes>
                <Route path="/" element={<Index />} />
            </Routes>
        </BrowserRouter>
    );
};

export default App;
