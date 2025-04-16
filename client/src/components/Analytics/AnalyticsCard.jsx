/**
 * File: client/src/components/Analytics/AnalyticsCard.jsx
 * Description: Component for displaying individual analytics metrics in a card format
 */

import React from 'react';

const AnalyticsCard = ({ title, value, subtitle, icon }) => {
  return (
    <div className="analytics-card">
      <div className="analytics-card-header">
        {icon && <div className="analytics-card-icon">{icon}</div>}
        <h4>{title}</h4>
      </div>
      <p className="analytics-value">{value}</p>
      {subtitle && <small>{subtitle}</small>}
    </div>
  );
};

export default AnalyticsCard;
