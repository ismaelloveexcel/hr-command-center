import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <main className="home-page" id="main-content">
      <h1>UAE HR Portal</h1>
      <p className="home-subtitle">
        Track your existing HR requests and stay updated on progress.
      </p>

      <div className="home-actions">
        <Link to="/track" className="action-card">
          <h2>
            <span role="img" aria-hidden="true">🔍</span>
            Track My Request
          </h2>
          <p>Check the status of your submitted request using your reference number (e.g., REF-2026-001)</p>
        </Link>
      </div>

      <div className="home-info">
        <h3>How It Works</h3>
        <ol>
          <li>Submit your request to HR</li>
          <li>Receive a unique reference number</li>
          <li>Track your request status anytime</li>
          <li>Get notified when status changes</li>
        </ol>
      </div>
    </main>
  );
}

export default Home;
