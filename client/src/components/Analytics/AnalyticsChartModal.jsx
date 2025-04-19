import React from 'react';
import {
  ScatterChart, Scatter, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend
} from 'recharts';

const AnalyticsChartModal = ({
  open,
  onClose,
  data = [],
  title = '',
  xKey = '',
  yKey = '',
  xLabel = '',
  yLabel = '',
  chartType = 'scatter', // 'scatter' or 'line'
  lineColor = '#8884d8',
  scatterColor = '#c3002f',
  name = 'Data',
}) => {
  if (!open) return null;

  const hasData = Array.isArray(data) && data.length > 0;

  return (
    <div className="analytics-modal-overlay">
      <div className="analytics-modal" style={{ maxWidth: 800, width: '98%' }}>
        <div className="analytics-modal-header">
          <h3>{title}</h3>
          <button className="close-button" onClick={onClose}>&times;</button>
        </div>
        <div className="analytics-modal-body">
          {!hasData ? (
            <div style={{ textAlign: 'center', color: '#888', padding: 40 }}>No data available.</div>
          ) : (
            <ResponsiveContainer width="100%" height={350}>
              {chartType === 'scatter' ? (
                <ScatterChart margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey={xKey} type="number" tick={{ fontSize: 12 }} label={{ value: xLabel, position: 'insideBottom', fontSize: 14 }} />
                  <YAxis dataKey={yKey} tick={{ fontSize: 12 }} label={{ value: yLabel, angle: -90, position: 'insideLeft', fontSize: 14 }} />
                  <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Legend />
                  <Scatter name={name} data={data} fill={scatterColor} />
                </ScatterChart>
              ) : (
                <LineChart data={data} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey={xKey} tick={{ fontSize: 12 }} label={{ value: xLabel, position: 'insideBottom', fontSize: 14 }} />
                  <YAxis dataKey={yKey} tick={{ fontSize: 12 }} label={{ value: yLabel, angle: -90, position: 'insideLeft', fontSize: 14 }} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey={yKey} stroke={lineColor} dot={false} name={name} />
                </LineChart>
              )}
            </ResponsiveContainer>
          )}
        </div>
      </div>
    </div>
  );
};

export default AnalyticsChartModal;
