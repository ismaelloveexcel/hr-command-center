import React, { useState, useEffect } from 'react';
import './HRQueue.css';
import { config } from '../config';

function HRQueue() {
  const [requests, setRequests] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [updateForm, setUpdateForm] = useState({
    status: '',
    public_notes: '',
    internal_notes: '',
    reviewed_by: 'hr.staff@company.ae'
  });

  useEffect(() => {
    fetchRequests();
    fetchStats();
  }, [filter]);

  const fetchRequests = async () => {
    setLoading(true);
    setError(null);

    try {
      const url = filter === 'all' 
        ? `${config.apiUrl}/requests`
        : `${config.apiUrl}/requests?status=${filter}`;
      
      const response = await fetch(url);
      
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

  const fetchStats = async () => {
    try {
      const response = await fetch(`${config.apiUrl}/hr/stats`);
      const data = await response.json();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const handleUpdateRequest = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch(
        `${config.apiUrl}/requests/${selectedRequest.reference}/status`,
        {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updateForm)
        }
      );

      if (!response.ok) {
        throw new Error('Failed to update request');
      }

      // Refresh data
      await fetchRequests();
      await fetchStats();
      setSelectedRequest(null);
      setUpdateForm({
        status: '',
        public_notes: '',
        internal_notes: '',
        reviewed_by: 'hr.staff@company.ae'
      });

      alert('Request updated successfully!');
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  };

  const openUpdateModal = (request) => {
    setSelectedRequest(request);
    setUpdateForm({
      status: request.status,
      public_notes: request.public_notes || '',
      internal_notes: request.internal_notes || '',
      reviewed_by: 'hr.staff@company.ae'
    });
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

  const getStatusBadge = (status) => {
    const badges = {
      submitted: { text: 'Submitted', class: 'badge-submitted' },
      reviewing: { text: 'Reviewing', class: 'badge-reviewing' },
      approved: { text: 'Approved', class: 'badge-approved' },
      completed: { text: 'Completed', class: 'badge-completed' },
      rejected: { text: 'Rejected', class: 'badge-rejected' }
    };
    const badge = badges[status] || { text: status, class: '' };
    return <span className={`status-badge ${badge.class}`}>{badge.text}</span>;
  };

  return (
    <main className="hr-queue">
      <h1>HR Request Queue</h1>

      {stats && (
        <div className="stats-bar">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Requests</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.status_counts.submitted}</div>
            <div className="stat-label">Pending Review</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.status_counts.reviewing}</div>
            <div className="stat-label">Under Review</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.status_counts.approved}</div>
            <div className="stat-label">Approved</div>
          </div>
        </div>
      )}

      <div className="filter-bar">
        <button 
          className={filter === 'all' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button 
          className={filter === 'submitted' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('submitted')}
        >
          Submitted
        </button>
        <button 
          className={filter === 'reviewing' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('reviewing')}
        >
          Reviewing
        </button>
        <button 
          className={filter === 'approved' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('approved')}
        >
          Approved
        </button>
        <button 
          className={filter === 'completed' ? 'filter-btn active' : 'filter-btn'}
          onClick={() => setFilter('completed')}
        >
          Completed
        </button>
      </div>

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
                      <span className="separator">•</span>
                      <span>{formatDate(request.submitted_at)}</span>
                    </div>
                  </div>
                  {getStatusBadge(request.status)}
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
                  {request.public_notes && (
                    <div className="info-row">
                      <strong>Public Notes:</strong> {request.public_notes}
                    </div>
                  )}
                  {request.internal_notes && (
                    <div className="info-row internal">
                      <strong>Internal Notes (HR only):</strong> {request.internal_notes}
                    </div>
                  )}
                </div>

                <button 
                  className="update-btn"
                  onClick={() => openUpdateModal(request)}
                >
                  Update Request
                </button>
              </div>
            ))
          )}
        </div>
      )}

      {selectedRequest && (
        <div className="modal-overlay" onClick={() => setSelectedRequest(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>Update Request</h2>
            <p className="modal-reference">{selectedRequest.reference}</p>

            <form onSubmit={handleUpdateRequest}>
              <div className="form-group">
                <label>Status</label>
                <select
                  value={updateForm.status}
                  onChange={(e) => setUpdateForm({...updateForm, status: e.target.value})}
                  required
                >
                  <option value="submitted">Submitted</option>
                  <option value="reviewing">Reviewing</option>
                  <option value="approved">Approved</option>
                  <option value="completed">Completed</option>
                  <option value="rejected">Rejected</option>
                </select>
              </div>

              <div className="form-group">
                <label>Public Notes (visible to employee)</label>
                <textarea
                  value={updateForm.public_notes}
                  onChange={(e) => setUpdateForm({...updateForm, public_notes: e.target.value})}
                  rows={3}
                  placeholder="Add notes that the employee can see..."
                />
              </div>

              <div className="form-group">
                <label>Internal Notes (HR only)</label>
                <textarea
                  value={updateForm.internal_notes}
                  onChange={(e) => setUpdateForm({...updateForm, internal_notes: e.target.value})}
                  rows={3}
                  placeholder="Add internal notes (not visible to employee)..."
                />
              </div>

              <div className="modal-actions">
                <button type="button" onClick={() => setSelectedRequest(null)}>
                  Cancel
                </button>
                <button type="submit" className="submit-btn">
                  Update Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

export default HRQueue;
