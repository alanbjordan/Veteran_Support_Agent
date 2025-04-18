import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const AnalyticsLatencyModal = ({ open, onClose, requests }) => {
  if (!open) return null;

  // Prepare chart data: token count on x-axis, latency on y-axis
  const chartData = (requests || [])
    .filter(req => req.latency_ms !== undefined && req.sentTokens !== undefined && req.receivedTokens !== undefined)
    .map(req => ({
      totalTokens: (req.sentTokens ?? 0) + (req.receivedTokens ?? 0),
      latency: req.latency_ms ?? req.latency ?? 0
    }));

  return (
    <div className="analytics-modal-overlay">
      <div className="analytics-modal" style={{ maxWidth: 800, width: '98%' }}>
        <div className="analytics-modal-header">
          <h3>Latency by Token Count</h3>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>
        <div className="analytics-modal-body">
          {chartData.length === 0 ? (
            <div style={{ textAlign: 'center', color: '#888', padding: 40 }}>No request data available.</div>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              <ScatterChart margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="totalTokens" type="number" tick={{ fontSize: 12 }} label={{ value: 'Total Tokens', position: 'insideBottom', fontSize: 14 }} />
                <YAxis dataKey="latency" tick={{ fontSize: 12 }} label={{ value: 'Latency (ms)', angle: -90, position: 'insideLeft', fontSize: 14 }} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter name="Requests" data={chartData} fill="#c3002f" />
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsLatencyModal;
