import React, { useState, useEffect } from 'react';
import './ComplianceCalendar.css';
import { config } from '../config';

function ComplianceCalendar() {
  const [events, setEvents] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [daysAhead, setDaysAhead] = useState(60);

  useEffect(() => {
    fetchData();
  }, [daysAhead]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [eventsRes, summaryRes] = await Promise.all([
        fetch(`${config.apiUrl}/compliance/events?days_ahead=${daysAhead}`),
        fetch(`${config.apiUrl}/compliance/summary?days_ahead=${daysAhead}`)
      ]);

      if (!eventsRes.ok || !summaryRes.ok) {
        throw new Error('Failed to fetch compliance data');
      }

      const eventsData = await eventsRes.json();
      const summaryData = await summaryRes.json();

      setEvents(eventsData);
      setSummary(summaryData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-AE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getDaysUntil = (dateString) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const eventDate = new Date(dateString);
    eventDate.setHours(0, 0, 0, 0);
    const diffTime = eventDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getSeverityClass = (severity) => {
    return `severity-${severity}`;
  };

  const getEventTypeLabel = (type) => {
    const labels = {
      wps_deadline: 'WPS Deadline',
      visa_expiry: 'Visa Expiry',
      emirates_id_expiry: 'Emirates ID Expiry',
      medical_expiry: 'Medical Expiry',
      ramadan_hours: 'Ramadan Hours'
    };
    return labels[type] || type;
  };

  return (
    <main className="compliance-calendar">
      <div className="calendar-header">
        <h1>UAE Compliance Calendar</h1>
        <div className="view-controls">
          <button
            className={daysAhead === 30 ? 'active' : ''}
            onClick={() => setDaysAhead(30)}
          >
            30 Days
          </button>
          <button
            className={daysAhead === 60 ? 'active' : ''}
            onClick={() => setDaysAhead(60)}
          >
            60 Days
          </button>
        </div>
      </div>

      {summary && (
        <div className="summary-cards">
          <div className="summary-card">
            <div className="card-value">{summary.total_events}</div>
            <div className="card-label">Total Events</div>
          </div>
          <div className="summary-card critical">
            <div className="card-value">{summary.critical_count}</div>
            <div className="card-label">Critical</div>
          </div>
          <div className="summary-card warning">
            <div className="card-value">{summary.warning_count}</div>
            <div className="card-label">Warnings</div>
          </div>
          <div className="summary-card upcoming">
            <div className="card-value">{summary.upcoming_7_days}</div>
            <div className="card-label">Next 7 Days</div>
          </div>
        </div>
      )}

      {error && <div className="error-message">{error}</div>}

      {loading ? (
        <div className="loading">Loading compliance calendar...</div>
      ) : (
        <div className="events-list">
          {events.length === 0 ? (
            <div className="no-events">
              <p>No upcoming compliance events in the next {daysAhead} days.</p>
              <p className="no-events-subtitle">All caught up! 🎉</p>
            </div>
          ) : (
            events.map((event) => {
              const daysUntil = getDaysUntil(event.event_date);
              const isUrgent = daysUntil <= 7;

              return (
                <div
                  key={event.id}
                  className={`event-card ${getSeverityClass(event.severity)} ${isUrgent ? 'urgent' : ''}`}
                >
                  <div className="event-header">
                    <div className="event-type">
                      {getEventTypeLabel(event.event_type)}
                    </div>
                    <div className="event-date">
                      <div className="days-until">
                        {daysUntil === 0 ? 'TODAY' : 
                         daysUntil === 1 ? 'TOMORROW' :
                         `${daysUntil} days`}
                      </div>
                      <div className="full-date">{formatDate(event.event_date)}</div>
                    </div>
                  </div>

                  <h3 className="event-title">{event.title}</h3>

                  {event.description && (
                    <p className="event-description">{event.description}</p>
                  )}

                  {event.related_entity && (
                    <div className="event-entity">
                      Related: {event.related_entity}
                    </div>
                  )}

                  {event.severity === 'critical' && (
                    <div className="critical-notice">
                      ⚠️ Urgent action required
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      )}
    </main>
  );
}

export default ComplianceCalendar;
