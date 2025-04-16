/**
 * File: client/src/components/Analytics/AnalyticsTable.jsx
 * Description: Component for displaying analytics data in a tabular format
 */

import React from 'react';

const AnalyticsTable = ({ requests }) => {
  return (
    <div className="analytics-table">
      <div className="analytics-table-header">
        <h3>Recent Requests</h3>
        <span className="total-requests">Total: {requests.length}</span>
      </div>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Model</th>
            <th>Sent</th>
            <th>Recv</th>
            <th>Total</th>
            <th>Cost</th>
            <th>Latency</th>
          </tr>
        </thead>
        <tbody>
          {requests.map((request, index) => {
            // Ensure cost is a number
            const cost = typeof request.cost === 'number' ? request.cost : 0;
            
            return (
              <tr key={index}>
                <td>{request.date}</td>
                <td>{request.model}</td>
                <td>{request.sentTokens.toLocaleString()}</td>
                <td>{request.receivedTokens.toLocaleString()}</td>
                <td>{(request.sentTokens + request.receivedTokens).toLocaleString()}</td>
                <td>${cost.toFixed(5)}</td>
                <td>{request.latency_ms}ms</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default AnalyticsTable;
