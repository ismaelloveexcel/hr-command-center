import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import Home from './pages/Home';
import TrackRequest from './pages/TrackRequest';
import HRQueue from './pages/HRQueue';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <nav>
          <ul>
            <li><Link to="/">Home</Link></li>
            <li><Link to="/track">Track My Request</Link></li>
            <li><Link to="/hr">HR Dashboard</Link></li>
          </ul>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/track" element={<TrackRequest />} />
          <Route path="/hr" element={<HRQueue />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
