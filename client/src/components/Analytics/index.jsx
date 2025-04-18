/**
 * File: client/src/components/Analytics/index.jsx
 * Description: Main analytics component that serves as the container for analytics features
 */

// client/src/components/Analytics/index.jsx

import React, { useState, useEffect, useRef } from 'react';
import AnalyticsSummary from './AnalyticsSummary';
import AnalyticsTable from './AnalyticsTable';
import AnalyticsRequestModal from './AnalyticsRequestModal';
import AnalyticsLatencyModal from './AnalyticsLatencyModal';
import apiClient from '../../utils/apiClient';
import './Analytics.css';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState({
    totalCost: 0,
    totalRequests: 0,
    averageCostPerRequest: 0,
    totalSentTokens: 0,
    totalReceivedTokens: 0,
    averageLatency: 0,
    requestsByDate: [],
    costByModel: {}
  });
  const [error, setError] = useState(null);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState(null);
  const [showLatencyModal, setShowLatencyModal] = useState(false);
  const lastDataRef = useRef(null);

  // Function to fetch analytics data
  const fetchAnalyticsData = async () => {
    setIsFetching(true);
    try {
      // Add a 1 second delay for better UX
      await new Promise(resolve => setTimeout(resolve, 1000));
      const response = await apiClient.get('/analytics/summary');
      const newData = response.data;
      console.log('Fetched analytics data:', newData);
      setAnalyticsData(newData);
      lastDataRef.current = newData;
      setError(null);
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setError('Failed to load analytics data. Please try again later.');
    } finally {
      setIsFetching(false);
    }
  };

  const handleReset = async () => {
    try {
      // Immediately clear the data
      const emptyData = {
        totalCost: 0,
        totalRequests: 0,
        averageCostPerRequest: 0,
        totalSentTokens: 0,
        totalReceivedTokens: 0,
        averageLatency: 0,
        requestsByDate: [],
        costByModel: {}
      };
      
      // Update the UI immediately with empty data
      setAnalyticsData(emptyData);
      lastDataRef.current = emptyData;
      setShowResetConfirm(false);
      
      // Then make the API call in the background
      const response = await apiClient.post('/analytics/reset');
      
      // Update with the actual reset data from the server
      if (response.data && response.data.analytics) {
        setAnalyticsData(response.data.analytics);
        lastDataRef.current = response.data.analytics;
      }
    } catch (err) {
      console.error('Error resetting analytics data:', err);
      setError('Failed to reset analytics data. Please try again later.');
    }
  };

  // Initial fetch
  useEffect(() => {
    fetchAnalyticsData();
  }, []);

  if (error) {
    return (
      <div className="analytics-container">
        <div className="error">{error}</div>
      </div>
    );
  }

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <h2>Model Performance Analytics</h2>
        <div className="header-buttons">
          <div style={{ display: 'flex', alignItems: 'center' }}>
            {isFetching && (
              <div className="loading-bar" style={{ marginRight: 8 }}>
                <span className="loading-text">Loading...</span>
              </div>
            )}
            <button 
              className="fetch-button"
              onClick={fetchAnalyticsData}
              disabled={isFetching}
            >
              {isFetching ? 'Fetching...' : 'Fetch Data'}
            </button>
          </div>
          <button 
            className="reset-button"
            onClick={() => setShowResetConfirm(true)}
          >
            Reset Data
          </button>
        </div>
      </div>

      {showResetConfirm && (
        <div className="reset-confirm-dialog">
          <div className="reset-confirm-content">
            <h3>Reset Analytics Data</h3>
            <p>Are you sure you want to reset all analytics data? This action cannot be undone.</p>
            <div className="reset-confirm-buttons">
              <button 
                className="cancel-button"
                onClick={() => setShowResetConfirm(false)}
              >
                Cancel
              </button>
              <button 
                className="confirm-button"
                onClick={handleReset}
              >
                Reset Data
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="analytics-content">
        <AnalyticsSummary 
          data={analyticsData} 
          onLatencyClick={() => setShowLatencyModal(true)} 
        />
        <AnalyticsTable 
          requests={analyticsData.requestsByDate} 
          onRowClick={setSelectedRequest}
        />
      </div>
      {selectedRequest && (
        <AnalyticsRequestModal 
          request={selectedRequest} 
          onClose={() => setSelectedRequest(null)} 
        />
      )}
      {showLatencyModal && (
        <AnalyticsLatencyModal
          open={showLatencyModal}
          onClose={() => setShowLatencyModal(false)}
          requests={analyticsData.requestsByDate}
        />
      )}
    </div>
  );
};

export default Analytics;
