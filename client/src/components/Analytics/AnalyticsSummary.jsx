import React from 'react';
import AnalyticsCard from './AnalyticsCard';

const AnalyticsSummary = ({ data }) => {
  // Add null checks for all values
  const totalCost = data?.totalCost || 0;
  const averageCostPerRequest = data?.averageCostPerRequest || 0;
  const totalRequests = data?.totalRequests || 0;
  const totalSentTokens = data?.totalSentTokens || 0;
  const totalReceivedTokens = data?.totalReceivedTokens || 0;
  const averageLatency = data?.averageLatency || 0;

  return (
    <div className="analytics-summary">
      <AnalyticsCard 
        title="Cost" 
        value={`$${totalCost.toFixed(4)}`} 
        subtitle={`Avg: $${averageCostPerRequest.toFixed(4)}/req`} 
      />
      <AnalyticsCard 
        title="Requests" 
        value={totalRequests} 
      />
      <AnalyticsCard 
        title="Sent Tokens" 
        value={totalSentTokens.toLocaleString()} 
      />
      <AnalyticsCard 
        title="Received Tokens" 
        value={totalReceivedTokens.toLocaleString()} 
      />
      <AnalyticsCard 
        title="Avg Latency" 
        value={`${averageLatency.toFixed(0)}ms`} 
        subtitle="Response Time"
      />
    </div>
  );
};

export default AnalyticsSummary;
