import React, { useState } from 'react';
import './TrackRequest.css';
import { config } from '../config';

function TrackRequest() {
  const [reference, setReference] = useState('');
  const [tracking, setTracking] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleTrack = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setTracking(null);

    try {
      const response = await fetch(`${config.apiUrl}/requests/track/${reference}`);
      
      if (!response.ok) {
        throw new Error('Request not found. Please check your reference number.');
      }

      const data = await response.json();
      setTracking(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-AE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <main className="track-request">
      <h1>Track My Request</h1>
      <p className="subtitle">Enter your request reference number to check its status</p>

      <form onSubmit={handleTrack} className="track-form">
        <div className="input-group">
          <input
            type="text"
            value={reference}
            onChange={(e) => setReference(e.target.value.toUpperCase())}
            placeholder="Enter reference (e.g., REF-2026-001)"
            className="reference-input"
            required
          />
          <button type="submit" disabled={loading} className="track-button">
            {loading ? 'Tracking...' : 'Track Request'}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      {tracking && (
        <div className="tracking-result">
          <div className="request-header">
            <h2>{tracking.title}</h2>
            <div className="reference-badge">{tracking.reference}</div>
          </div>

          <div className={`status-card status-${tracking.current_status}`}>
            <div className="status-label">{tracking.status_label}</div>
            {tracking.next_steps && (
              <div className="next-steps">{tracking.next_steps}</div>
            )}
          </div>

          {tracking.description && (
            <div className="description-section">
              <h3>Request Details</h3>
              <p>{tracking.description}</p>
            </div>
          )}

          <div className="timeline-section">
            <h3>Request Timeline</h3>
            <div className="timeline">
              {tracking.timeline.map((event, index) => (
                <div key={index} className="timeline-event">
                  <div className="timeline-dot"></div>
                  <div className="timeline-content">
                    <div className="timeline-date">{formatDate(event.timestamp)}</div>
                    <div className="timeline-description">{event.description}</div>
                    {event.notes && (
                      <div className="timeline-notes">{event.notes}</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="meta-info">
            <p><strong>Submitted by:</strong> {tracking.submitted_by}</p>
            <p><strong>Last updated:</strong> {formatDate(tracking.last_updated)}</p>
          </div>
        </div>
      )}
    </main>
  );
}

export default TrackRequest;
