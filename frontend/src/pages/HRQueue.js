import React, { useState, useEffect } from 'react';
import './HRQueue.css';
import { config } from '../config';

function HRQueue() {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingRef, setUpdatingRef] = useState(null);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${config.apiUrl}/requests`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch requests');
      }

      const data = await response.json();
      setRequests(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (reference, newStatus) => {
    setUpdatingRef(reference);

    try {
      const response = await fetch(
        `${config.apiUrl}/requests/${reference}/status`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: newStatus })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update status');
      }

      await fetchRequests();
    } catch (err) {
      alert(`Error: ${err.message}`);
    } finally {
      setUpdatingRef(null);
    }
  };

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
    <main className="hr-queue">
      <div className="page-header">
        <h1>HR Dashboard</h1>
        <p className="subtitle">Manage and update employee request statuses</p>
      </div>

      {error && (
        <div className="error-message">
          <span className="error-icon">!</span>
          <p>{error}</p>
          <button onClick={fetchRequests} className="retry-btn">Retry</button>
        </div>
      )}

      {loading ? (
        renderSkeletons()
      ) : requests.length === 0 ? (
        renderEmptyState()
      ) : (
        <div className="requests-list">
          {requests.map((request) => (
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
                    <span className="status-dot">{getStatusIcon(request.status)}</span>
                  </div>
                  <select
                    value={request.status}
                    onChange={(e) => handleStatusChange(request.reference, e.target.value)}
                    disabled={updatingRef === request.reference}
                    className={`status-select ${request.status}`}
                  >
                    <option value="submitted">Submitted</option>
                    <option value="reviewing">Reviewing</option>
                    <option value="approved">Approved</option>
                    <option value="completed">Completed</option>
                    <option value="rejected">Rejected</option>
                  </select>
                  {updatingRef === request.reference && (
                    <span className="updating-spinner"></span>
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
          ))}
        </div>
      )}
    </main>
  );
}

export default HRQueue;
