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
      const response = await fetch(`${config.apiUrl}/requests/${reference}`);
      
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

  const getStatusIcon = (status) => {
    const icons = {
      submitted: '●',
      reviewing: '◐',
      approved: '✓',
      completed: '✓✓',
      rejected: '✕'
    };
    return icons[status] || '●';
  };

  return (
    <main className="track-request">
      <div className="track-header">
        <h1>Track My Request</h1>
        <p className="subtitle">Enter your reference number to check the status of your request</p>
      </div>

      <form onSubmit={handleTrack} className="track-form">
        <div className="input-wrapper">
          <input
            type="text"
            id="reference"
            value={reference}
            onChange={(e) => setReference(e.target.value.toUpperCase())}
            placeholder=" "
            className="reference-input"
            required
          />
          <label htmlFor="reference" className="floating-label">Reference Number</label>
          <span className="input-hint">e.g., REF-2026-001</span>
        </div>
        <button type="submit" disabled={loading} className="track-button">
          {loading ? (
            <span className="button-loading">
              <span className="spinner"></span>
              Tracking...
            </span>
          ) : (
            'Track Request'
          )}
        </button>
      </form>

      <div className="helper-card">
        <h2>Need help finding your reference?</h2>
        <p>
          Your reference number is shared in the confirmation email from HR. If you no longer have it,
          contact your HR representative for assistance.
        </p>
      </div>

      {error && (
        <div className="error-message" role="alert" aria-live="polite">
          <span className="error-icon">!</span>
          <p>{error}</p>
        </div>
      )}

      {loading && !tracking && (
        <div className="loading-skeleton">
          <div className="skeleton-card">
            <div className="skeleton skeleton-line medium"></div>
            <div className="skeleton skeleton-line short"></div>
          </div>
          <div className="skeleton-card">
            <div className="skeleton skeleton-line long"></div>
            <div className="skeleton skeleton-line medium"></div>
            <div className="skeleton skeleton-line short"></div>
          </div>
        </div>
      )}

      {tracking && (
        <div className="tracking-result">
          <div className="request-header">
            <div>
              <h2>{tracking.title}</h2>
              <div className="reference-badge">{tracking.reference}</div>
            </div>
          </div>

          <div className={`status-card status-${tracking.current_status}`}>
            <div className="status-content">
              <span className={`status-icon-large ${tracking.current_status}`}>
                {getStatusIcon(tracking.current_status)}
              </span>
              <div>
                <div className="status-label">
                  Status: <span className="status-text">{tracking.status_label}</span>
                </div>
                {tracking.next_steps && (
                  <div className="next-steps">{tracking.next_steps}</div>
                )}
              </div>
            </div>
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
                <div 
                  key={index} 
                  className={`timeline-event ${index === tracking.timeline.length - 1 ? 'latest' : ''}`}
                >
                  <div className={`timeline-dot ${event.status}`}>
                    <span>{getStatusIcon(event.status)}</span>
                  </div>
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
            <div className="meta-item">
              <span className="meta-label">Last updated</span>
              <span className="meta-value">{formatDate(tracking.last_updated)}</span>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default TrackRequest;
