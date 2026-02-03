import React, { useState, useEffect, useCallback } from 'react';
import './HRQueue.css';
import { config } from '../config';

function HRQueue() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [updatingRef, setUpdatingRef] = useState(null);
  const [pendingStatuses, setPendingStatuses] = useState({});
  const [hrApiKey, setHrApiKey] = useState(() => sessionStorage.getItem('hrApiKey') || '');
  const [pendingKey, setPendingKey] = useState('');
  const [hasKey, setHasKey] = useState(() => Boolean(sessionStorage.getItem('hrApiKey')));
  const [reviewedBy, setReviewedBy] = useState(() => sessionStorage.getItem('hrReviewedBy') || '');

  const persistReviewer = useCallback((value) => {
    sessionStorage.setItem('hrReviewedBy', value);
  }, []);

  const invalidateKey = useCallback(() => {
    sessionStorage.removeItem('hrApiKey');
    setHrApiKey('');
    setHasKey(false);
    setPendingKey('');
    setRequests([]);
  }, []);

  const fetchRequests = useCallback(async () => {
    if (!hrApiKey) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${config.apiUrl}/hr/requests`, {
        headers: {
          'X-HR-API-Key': hrApiKey,
        },
      });
      
      if (response.status === 401) {
        throw new Error('Unauthorized: Invalid HR API key');
      }

      if (!response.ok) {
        throw new Error('Failed to fetch requests');
      }

      const data = await response.json();
      setRequests(data);
      setPendingStatuses({});
    } catch (err) {
      if (err.message.startsWith('Unauthorized')) {
        invalidateKey();
        setError('Invalid HR API key. Please enter a valid key to continue.');
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }, [hrApiKey, invalidateKey]);

  const handleStatusChange = async (reference, newStatus) => {
    if (!hrApiKey) {
      setError('HR API key required.');
      return;
    }

    setUpdatingRef(reference);
    setError(null);

    try {
      const payload = { status: newStatus };

      if (reviewedBy.trim()) {
        payload.reviewed_by = reviewedBy.trim();
      }

      const response = await fetch(
        `${config.apiUrl}/requests/${reference}/status`,
        {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-HR-API-Key': hrApiKey,
          },
          body: JSON.stringify(payload)
        }
      );

      if (response.status === 401) {
        throw new Error('Unauthorized: Invalid HR API key');
      }

      if (!response.ok) {
        throw new Error('Failed to update status');
      }

      await fetchRequests();
    } catch (err) {
      if (err.message.startsWith('Unauthorized')) {
        invalidateKey();
        setError('HR API key expired or invalid. Please re-enter it.');
      } else {
        setError(err.message);
      }
    } finally {
      setUpdatingRef(null);
    }
  };

  useEffect(() => {
    if (hasKey && hrApiKey) {
      fetchRequests();
    }
  }, [hasKey, hrApiKey, fetchRequests]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-AE', {
      year: 'numeric',
      month: 'short',
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

  const handleKeySubmit = (event) => {
    event.preventDefault();
    const trimmed = pendingKey.trim();
    if (!trimmed) {
      setError('Please provide a valid HR API key.');
      return;
    }
    sessionStorage.setItem('hrApiKey', trimmed);
    setHrApiKey(trimmed);
    setHasKey(true);
    setPendingKey('');
    setError(null);
  };

  const handleResetKey = () => {
    invalidateKey();
    setError(null);
  };

  const handleReviewerChange = (event) => {
    const value = event.target.value;
    setReviewedBy(value);
    persistReviewer(value);
  };

  const handleClearReviewer = () => {
    setReviewedBy('');
    persistReviewer('');
  };

  const renderSkeletons = () => (
    <div className="skeleton-container">
      {[1, 2, 3].map((i) => (
        <div key={i} className="skeleton-card">
          <div className="skeleton-header">
            <div className="skeleton skeleton-line medium"></div>
            <div className="skeleton skeleton-badge"></div>
          </div>
          <div className="skeleton skeleton-line long"></div>
          <div className="skeleton skeleton-line short"></div>
        </div>
      ))}
    </div>
  );

  const renderEmptyState = () => (
    <div className="empty-state">
      <div className="empty-state-icon">📋</div>
      <h3>No Requests Yet</h3>
      <p>When employees submit requests, they will appear here for review.</p>
    </div>
  );

  return (
    <main className="hr-queue" id="main-content">
      <div className="page-header">
        <h1>HR Dashboard (staff only)</h1>
        <p className="subtitle">Manage and update employee request statuses securely</p>
      </div>

      {!hasKey ? (
        <div className="hr-key-gate">
          <h2>Restricted Access</h2>
          <p className="gate-note">Enter the HR API key to unlock the dashboard.</p>
          <p className="gate-warning">Do not enter this key on shared or public devices.</p>
          <p className="gate-session">This key is stored for this browser session only.</p>
          {error && (
            <p className="gate-error" role="alert" aria-live="polite">{error}</p>
          )}
          <form onSubmit={handleKeySubmit}>
            <label htmlFor="hr-api-key">HR API Key</label>
            <input
              id="hr-api-key"
              type="password"
              value={pendingKey}
              onChange={(event) => setPendingKey(event.target.value)}
              placeholder="Paste the key provided by your administrator"
              autoComplete="off"
            />
            <button type="submit" className="unlock-btn">Unlock Dashboard</button>
          </form>
        </div>
      ) : (
        <>
          {error && (
            <div className="error-message" role="alert" aria-live="polite">
              <span className="error-icon">!</span>
              <p>{error}</p>
              <button onClick={fetchRequests} className="retry-btn">Retry</button>
            </div>
          )}

          <div className="hr-toolbar">
            <div className="reviewer-form">
              <label htmlFor="reviewer-input">Reviewer (optional)</label>
              <input
                id="reviewer-input"
                type="text"
                value={reviewedBy}
                onChange={handleReviewerChange}
                placeholder="Name or email recorded with each update"
              />
              {reviewedBy && (
                <button type="button" onClick={handleClearReviewer} className="clear-reviewer-btn">
                  Clear
                </button>
              )}
            </div>
            <button type="button" onClick={handleResetKey} className="reset-key-btn">
              Log out (clear key)
            </button>
          </div>

          {loading ? (
            renderSkeletons()
          ) : requests.length === 0 ? (
            renderEmptyState()
          ) : (
            <div className="requests-list">
              {requests.map((request) => {
                const pendingStatus = pendingStatuses[request.reference] ?? request.status;
                return (
                  <div key={request.id} className={`request-card status-${request.status}`}>
                  <div className="card-accent"></div>
                  <div className="request-header">
                    <div className="request-title-section">
                      <h3>{request.title}</h3>
                      <div className="request-meta">
                        <span className="reference">{request.reference}</span>
                        <span className="separator">•</span>
                        <span className="date">{formatDate(request.submitted_at)}</span>
                      </div>
                    </div>
                    <div className="status-control">
                      <div className={`status-indicator ${request.status}`}>
                        <span className="status-dot" aria-hidden="true">{getStatusIcon(request.status)}</span>
                      </div>
                      <div className="status-text">
                        Status: {request.status_label || request.status}
                      </div>
                      <label className="status-select-label" htmlFor={`status-${request.reference}`}>
                        Update status
                      </label>
                      <select
                        id={`status-${request.reference}`}
                        value={pendingStatus}
                        onChange={(e) => setPendingStatuses((prev) => ({
                          ...prev,
                          [request.reference]: e.target.value
                        }))}
                        disabled={updatingRef === request.reference}
                        className={`status-select ${pendingStatus}`}
                      >
                        <option value="submitted">Submitted</option>
                        <option value="reviewing">Reviewing</option>
                        <option value="approved">Approved</option>
                        <option value="completed">Completed</option>
                        <option value="rejected">Rejected</option>
                      </select>
                      <button
                        type="button"
                        className="apply-status-btn"
                        onClick={() => handleStatusChange(request.reference, pendingStatus)}
                        disabled={updatingRef === request.reference || pendingStatus === request.status}
                      >
                        Apply
                      </button>
                      {updatingRef === request.reference && (
                        <span className="updating-spinner" aria-hidden="true"></span>
                      )}
                    </div>
                  </div>

                  {request.description && (
                    <p className="request-description">{request.description}</p>
                  )}

                  <div className="request-details">
                    <div className="detail-item">
                      <span className="detail-label">Submitted by</span>
                      <span className="detail-value">{request.submitted_by}</span>
                    </div>
                    {request.reviewed_by && (
                      <div className="detail-item">
                        <span className="detail-label">Reviewed by</span>
                        <span className="detail-value">{request.reviewed_by}</span>
                      </div>
                    )}
                  </div>

                  {request.internal_notes && (
                    <div className="internal-notes">
                      <span className="notes-label">Internal Notes</span>
                      <p>{request.internal_notes}</p>
                    </div>
                  )}
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </main>
  );
}

export default HRQueue;
