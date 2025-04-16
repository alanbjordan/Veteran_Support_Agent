/**
 * File: client/src/App.js
 * Description: Main application component that serves as the root of the React application
 */

import './App.css';
import { BrowserRouter } from 'react-router-dom';
import AppLayout from './components/AppLayout';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <AppLayout />
      </div>
    </BrowserRouter>
  );
}

export default App;