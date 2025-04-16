import React, { useState } from 'react';
import './InventoryDisplay.css';

const InventoryDisplay = () => {
  const [isOpen, setIsOpen] = useState(false);

  const handleInventoryClick = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="inventory-display">
      <button 
        className="inventory-button"
        onClick={handleInventoryClick}
      >
        View Inventory
      </button>
      
      {isOpen && (
        <div className="inventory-modal">
          <div className="inventory-modal-content">
            <div className="inventory-modal-header">
              <h3>Current Inventory</h3>
              <button 
                className="close-button"
                onClick={() => setIsOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="inventory-modal-body">
              <p>Loading inventory data...</p>
              {/* Inventory data will be populated here */}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default InventoryDisplay; 