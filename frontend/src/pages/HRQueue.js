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

      // Refresh the list
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

  return (
    <main className="hr-queue">
      <h1>HR Dashboard</h1>
      <p className="subtitle">Manage employee requests</p>

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading requests...</div>
      ) : (
        <div className="requests-list">
          {requests.length === 0 ? (
            <div className="no-requests">No requests found</div>
          ) : (
            requests.map((request) => (
              <div key={request.id} className="request-card">
                <div className="request-header">
                  <div>
                    <h3>{request.title}</h3>
                    <div className="request-meta">
                      <span className="reference">{request.reference}</span>
                      <span className="separator">-</span>
                      <span>{formatDate(request.submitted_at)}</span>
                    </div>
                  </div>
                  <div className="status-control">
                    <select
                      value={request.status}
                      onChange={(e) => handleStatusChange(request.reference, e.target.value)}
                      disabled={updatingRef === request.reference}
                      className={`status-select status-${request.status}`}
                    >
                      <option value="submitted">Submitted</option>
                      <option value="reviewing">Reviewing</option>
                      <option value="approved">Approved</option>
                      <option value="completed">Completed</option>
                      <option value="rejected">Rejected</option>
                    </select>
                    {updatingRef === request.reference && (
                      <span className="updating">Updating...</span>
                    )}
                  </div>
                </div>

                {request.description && (
                  <p className="request-description">{request.description}</p>
                )}

                <div className="request-info">
                  <div className="info-row">
                    <strong>Submitted by:</strong> {request.submitted_by}
                  </div>
                  {request.reviewed_by && (
                    <div className="info-row">
                      <strong>Reviewed by:</strong> {request.reviewed_by}
                    </div>
                  )}
                  {request.internal_notes && (
                    <div className="info-row internal">
                      <strong>Internal Notes:</strong> {request.internal_notes}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      )}
    </main>
  );
}

export default HRQueue;
