import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
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