// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import NewsFeed from './pages/NewsFeed';

const App: React.FC = () => {
    return (
        <Router>
            <Routes>
                <Route path="/feed" element={<NewsFeed />} />
                {/* Add other routes here */}
            </Routes>
        </Router>
    );
};

export default App;
