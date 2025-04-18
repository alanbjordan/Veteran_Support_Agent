import React, { useEffect, useState } from 'react';
import apiClient from '../../utils/apiClient';
import './Analytics.css';

const AnalyticsRequestModal = ({ request, onClose }) => {
  const [openaiLog, setOpenaiLog] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (request && request.log_id) {
      setLoading(true);
      setError(null);
      apiClient.get(`/analytics/openai-log/${request.log_id}`)
        .then(res => setOpenaiLog(res.data))
        .catch(err => setError('Failed to load OpenAI log'))
        .finally(() => setLoading(false));
    } else {
      setOpenaiLog(null);
    }
  }, [request]);

  if (!request) return null;

  return (
    <div className="analytics-modal-overlay">
      <div className="analytics-modal">
        <div className="analytics-modal-header">
          <h3>OpenAI API Log</h3>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>
        <div className="analytics-modal-body">
          {loading && <div style={{marginTop:12}}>Loading OpenAI log...</div>}
          {error && <div style={{color:'red',marginTop:12}}>{error}</div>}
          {openaiLog && (
            <table className="analytics-modal-table">
              <tbody>
                <tr><th>Request Prompt</th><td style={{whiteSpace:'pre-wrap'}}>{openaiLog.request_prompt}</td></tr>
                <tr><th>Status</th><td>{openaiLog.status}</td></tr>
                <tr><th>Sent At</th><td>{openaiLog.request_sent_at}</td></tr>
                <tr><th>Received At</th><td>{openaiLog.response_received_at}</td></tr>
                <tr><th>Error</th><td>{openaiLog.error_message || 'None'}</td></tr>
                <tr><th>Request Payload</th><td><pre style={{maxHeight:120,overflow:'auto'}}>{JSON.stringify(openaiLog.request_payload, null, 2)}</pre></td></tr>
                <tr><th>Response JSON</th><td><pre style={{maxHeight:120,overflow:'auto'}}>{JSON.stringify(openaiLog.response_json, null, 2)}</pre></td></tr>
              </tbody>
            </table>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsRequestModal;
