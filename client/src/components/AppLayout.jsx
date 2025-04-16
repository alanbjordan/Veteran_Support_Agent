/**
 * File: client/src/components/AppLayout.jsx
 * Description: Main layout component that provides the structure for the application
 */

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Chat from './Chat/Chat';
import Analytics from './Analytics';

const AppLayout = () => {
  return (
    <Routes>
      <Route path="/" element={<Chat />} />
      <Route path="/analytics" element={<Analytics />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default AppLayout; 