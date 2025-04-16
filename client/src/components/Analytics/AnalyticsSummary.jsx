/**
 * File: client/src/components/Analytics/AnalyticsSummary.jsx
 * Description: Component for displaying analytics summary information
 */

import React from 'react';
import AnalyticsCard from './AnalyticsCard';
import { FaDollarSign, FaChartLine } from 'react-icons/fa';

const AnalyticsSummary = ({ data }) => {
  // Add null checks for all values
  const totalCost = data?.totalCost || 0;
  const averageCostPerRequest = data?.averageCostPerRequest || 0;
  const totalRequests = data?.totalRequests || 0;
  const totalSentTokens = data?.totalSentTokens || 0;
  const totalReceivedTokens = data?.totalReceivedTokens || 0;
  const averageLatency = data?.averageLatency || 0;
  const totalTokens = totalSentTokens + totalReceivedTokens;

  return (
    <div className="analytics-summary">
      {/* Top row - Cost metrics */}
      <div className="analytics-row">
        <AnalyticsCard
          title="Total Cost"
          value={`$${totalCost.toFixed(5)}`}
          icon={<FaDollarSign />}
        />
        <AnalyticsCard
          title="Average Cost"
          value={`$${averageCostPerRequest.toFixed(5)}/req`}
          icon={<FaChartLine />}
        />
        <AnalyticsCard 
          title="Avg Latency" 
          value={`${averageLatency.toFixed(0)}ms`}
          subtitle="Response Time"
        />
      </div>

      {/* Bottom row - Token metrics */}
      <div className="analytics-row">
        <AnalyticsCard 
          title="Total Tokens" 
          value={totalTokens.toLocaleString()} 
        />
        <AnalyticsCard 
          title="Sent Tokens" 
          value={totalSentTokens.toLocaleString()} 
        />
        <AnalyticsCard 
          title="Received Tokens" 
          value={totalReceivedTokens.toLocaleString()} 
        />
      </div>
    </div>
  );
};

export default AnalyticsSummary;
