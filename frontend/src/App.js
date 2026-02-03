import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import Home from './pages/Home';
import TrackRequest from './pages/TrackRequest';
import HRQueue from './pages/HRQueue';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <a href="#main-content" className="skip-link">Skip to main content</a>
        <nav aria-label="Primary">
          <div className="nav-container">
            <NavLink to="/" className="brand" end>UAE HR Portal</NavLink>
            <ul>
              <li><NavLink to="/" end>Home</NavLink></li>
              <li><NavLink to="/track">Track Request</NavLink></li>
            </ul>
          </div>
        </nav>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/track" element={<TrackRequest />} />
          <Route path="/hr" element={<HRQueue />} />
        </Routes>
        <footer>
          <p>UAE HR Portal - Employee Request Management System</p>
        </footer>
      </div>
    </Router>
  );
}

export default App;
