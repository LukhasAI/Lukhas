/**
 * Reasoning Lab Safety Admin Dashboard
 *
 * Admin interface for monitoring redaction statistics, configuring detection
 * thresholds, reviewing flagged traces, and exporting audit logs.
 */

import React, { useState, useEffect } from 'react';

interface RedactionStats {
  total_redactions: number;
  by_type: Record<string, number>;
  by_mode: Record<string, number>;
  last_updated: string;
}

interface FlaggedTrace {
  trace_id: string;
  detections_count: number;
  created_at: string;
  flagged_types: string[];
}

interface DetectionThreshold {
  type: string;
  threshold: number;
  description: string;
}

const ReasoningLabSafetyDashboard: React.FC = () => {
  const [stats, setStats] = useState<RedactionStats | null>(null);
  const [flaggedTraces, setFlaggedTraces] = useState<FlaggedTrace[]>([]);
  const [thresholds, setThresholds] = useState<DetectionThreshold[]>([
    { type: 'api_keys', threshold: 0.8, description: 'API Keys (OpenAI, Anthropic, AWS)' },
    { type: 'passwords', threshold: 0.7, description: 'Passwords and Secrets' },
    { type: 'pii', threshold: 0.6, description: 'Personal Identifiable Information' },
    { type: 'credit_cards', threshold: 0.9, description: 'Credit Card Numbers' },
  ]);
  const [selectedTimeRange, setSelectedTimeRange] = useState<string>('7d');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    fetchStatistics();
    fetchFlaggedTraces();
    const interval = setInterval(fetchStatistics, 60000); // Update every minute
    return () => clearInterval(interval);
  }, [selectedTimeRange]);

  const fetchStatistics = async () => {
    // In production, this would be an API call
    // Mock data for demonstration
    setLoading(true);
    try {
      const mockStats: RedactionStats = {
        total_redactions: 342,
        by_type: {
          'api_key_openai': 45,
          'api_key_anthropic': 23,
          'email': 127,
          'phone_number': 89,
          'credit_card': 12,
          'password': 46,
        },
        by_mode: {
          'full': 210,
          'partial': 78,
          'hash': 34,
          'blur': 20,
        },
        last_updated: new Date().toISOString(),
      };
      setStats(mockStats);
    } finally {
      setLoading(false);
    }
  };

  const fetchFlaggedTraces = async () => {
    // Mock flagged traces
    const mockTraces: FlaggedTrace[] = [
      {
        trace_id: 'trace-abc123',
        detections_count: 3,
        created_at: '2025-11-08T10:30:00Z',
        flagged_types: ['api_key_openai', 'email'],
      },
      {
        trace_id: 'trace-def456',
        detections_count: 1,
        created_at: '2025-11-08T09:15:00Z',
        flagged_types: ['credit_card'],
      },
    ];
    setFlaggedTraces(mockTraces);
  };

  const handleThresholdChange = (type: string, value: number) => {
    setThresholds((prev) =>
      prev.map((t) => (t.type === type ? { ...t, threshold: value } : t))
    );
  };

  const handleExportLogs = (format: 'csv' | 'json') => {
    // Export audit logs
    const data = {
      stats,
      flaggedTraces,
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob(
      [format === 'json' ? JSON.stringify(data, null, 2) : convertToCSV(data)],
      { type: format === 'json' ? 'application/json' : 'text/csv' }
    );

    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `reasoning_lab_audit_${Date.now()}.${format}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const convertToCSV = (data: any): string => {
    // Simple CSV conversion for demonstration
    return 'type,count\n' + Object.entries(data.stats?.by_type || {})
      .map(([k, v]) => `${k},${v}`)
      .join('\n');
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Reasoning Lab Safety Dashboard</h1>
        <p className="subtitle">Monitor redaction statistics and safety controls</p>
      </header>

      {/* Statistics Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Redactions</h3>
          <p className="stat-value">{stats?.total_redactions || 0}</p>
          <p className="stat-label">Last {selectedTimeRange}</p>
        </div>

        <div className="stat-card">
          <h3>Flagged Traces</h3>
          <p className="stat-value danger">{flaggedTraces.length}</p>
          <p className="stat-label">Requiring review</p>
        </div>

        <div className="stat-card">
          <h3>Detection Rate</h3>
          <p className="stat-value success">95.7%</p>
          <p className="stat-label">Average confidence</p>
        </div>

        <div className="stat-card">
          <h3>Demo Sessions</h3>
          <p className="stat-value">28</p>
          <p className="stat-label">Active now</p>
        </div>
      </div>

      {/* Redactions by Type */}
      <div className="section">
        <h2>Redactions by Type</h2>
        <div className="chart-container">
          {stats && (
            <div className="bar-chart">
              {Object.entries(stats.by_type)
                .sort(([, a], [, b]) => b - a)
                .map(([type, count]) => (
                  <div key={type} className="bar-item">
                    <div className="bar-label">{type.replace(/_/g, ' ')}</div>
                    <div className="bar-wrapper">
                      <div
                        className="bar-fill"
                        style={{
                          width: `${(count / stats.total_redactions) * 100}%`,
                        }}
                      />
                      <span className="bar-count">{count}</span>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>

      {/* Detection Thresholds Configuration */}
      <div className="section">
        <h2>Detection Sensitivity Thresholds</h2>
        <div className="thresholds-grid">
          {thresholds.map((threshold) => (
            <div key={threshold.type} className="threshold-item">
              <label>{threshold.description}</label>
              <div className="threshold-control">
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={threshold.threshold}
                  onChange={(e) =>
                    handleThresholdChange(threshold.type, parseFloat(e.target.value))
                  }
                />
                <span className="threshold-value">
                  {(threshold.threshold * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Flagged Traces */}
      <div className="section">
        <h2>Flagged Reasoning Traces</h2>
        <div className="table-container">
          <table className="traces-table">
            <thead>
              <tr>
                <th>Trace ID</th>
                <th>Detections</th>
                <th>Types Detected</th>
                <th>Created At</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {flaggedTraces.map((trace) => (
                <tr key={trace.trace_id}>
                  <td><code>{trace.trace_id}</code></td>
                  <td><span className="badge">{trace.detections_count}</span></td>
                  <td>{trace.flagged_types.join(', ')}</td>
                  <td>{new Date(trace.created_at).toLocaleString()}</td>
                  <td>
                    <button className="btn-small">Review</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Export Controls */}
      <div className="section">
        <h2>Export Audit Logs</h2>
        <div className="export-controls">
          <button
            className="btn-primary"
            onClick={() => handleExportLogs('json')}
          >
            Export as JSON
          </button>
          <button
            className="btn-secondary"
            onClick={() => handleExportLogs('csv')}
          >
            Export as CSV
          </button>
        </div>
      </div>

      {/* Styling */}
      <style jsx>{`
        .dashboard-container {
          max-width: 1400px;
          margin: 0 auto;
          padding: 2rem;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .dashboard-header {
          margin-bottom: 2rem;
        }

        .dashboard-header h1 {
          font-size: 2rem;
          font-weight: 700;
          color: #111827;
          margin-bottom: 0.5rem;
        }

        .subtitle {
          color: #6b7280;
          font-size: 1rem;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
          gap: 1.5rem;
          margin-bottom: 2rem;
        }

        .stat-card {
          background: white;
          padding: 1.5rem;
          border-radius: 0.5rem;
          border: 1px solid #e5e7eb;
          box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .stat-card h3 {
          font-size: 0.875rem;
          font-weight: 600;
          color: #6b7280;
          margin-bottom: 0.75rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }

        .stat-value {
          font-size: 2.5rem;
          font-weight: 700;
          color: #111827;
          margin-bottom: 0.25rem;
        }

        .stat-value.danger {
          color: #ef4444;
        }

        .stat-value.success {
          color: #10b981;
        }

        .stat-label {
          font-size: 0.875rem;
          color: #6b7280;
        }

        .section {
          background: white;
          padding: 1.5rem;
          border-radius: 0.5rem;
          border: 1px solid #e5e7eb;
          margin-bottom: 1.5rem;
        }

        .section h2 {
          font-size: 1.25rem;
          font-weight: 600;
          color: #111827;
          margin-bottom: 1rem;
        }

        .bar-chart {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .bar-item {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .bar-label {
          min-width: 150px;
          font-size: 0.875rem;
          color: #374151;
          text-transform: capitalize;
        }

        .bar-wrapper {
          flex: 1;
          position: relative;
          height: 24px;
          background: #f3f4f6;
          border-radius: 0.25rem;
        }

        .bar-fill {
          height: 100%;
          background: linear-gradient(90deg, #3b82f6, #60a5fa);
          border-radius: 0.25rem;
          transition: width 0.3s ease;
        }

        .bar-count {
          position: absolute;
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
          font-size: 0.75rem;
          font-weight: 600;
          color: #111827;
        }

        .thresholds-grid {
          display: grid;
          gap: 1rem;
        }

        .threshold-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background: #f9fafb;
          border-radius: 0.375rem;
        }

        .threshold-item label {
          font-size: 0.875rem;
          color: #374151;
          font-weight: 500;
        }

        .threshold-control {
          display: flex;
          align-items: center;
          gap: 1rem;
        }

        .threshold-control input[type='range'] {
          width: 200px;
        }

        .threshold-value {
          min-width: 40px;
          text-align: right;
          font-weight: 600;
          color: #111827;
        }

        .traces-table {
          width: 100%;
          border-collapse: collapse;
        }

        .traces-table th {
          text-align: left;
          padding: 0.75rem;
          background: #f9fafb;
          font-size: 0.875rem;
          font-weight: 600;
          color: #374151;
          border-bottom: 2px solid #e5e7eb;
        }

        .traces-table td {
          padding: 0.75rem;
          border-bottom: 1px solid #e5e7eb;
          font-size: 0.875rem;
          color: #111827;
        }

        .badge {
          display: inline-block;
          padding: 0.25rem 0.5rem;
          background: #fef3c7;
          color: #92400e;
          border-radius: 0.25rem;
          font-weight: 600;
          font-size: 0.75rem;
        }

        .btn-small {
          padding: 0.25rem 0.75rem;
          font-size: 0.875rem;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 0.25rem;
          cursor: pointer;
        }

        .btn-small:hover {
          background: #2563eb;
        }

        .export-controls {
          display: flex;
          gap: 1rem;
        }

        .btn-primary,
        .btn-secondary {
          padding: 0.75rem 1.5rem;
          font-size: 0.875rem;
          font-weight: 600;
          border-radius: 0.375rem;
          border: none;
          cursor: pointer;
          transition: all 0.2s;
        }

        .btn-primary {
          background: #3b82f6;
          color: white;
        }

        .btn-primary:hover {
          background: #2563eb;
        }

        .btn-secondary {
          background: #f3f4f6;
          color: #374151;
          border: 1px solid #d1d5db;
        }

        .btn-secondary:hover {
          background: #e5e7eb;
        }
      `}</style>
    </div>
  );
};

export default ReasoningLabSafetyDashboard;
