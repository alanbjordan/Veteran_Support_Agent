/**
 * File: client/src/components/Chat/ChatInput.jsx
 * Description: Component for handling user input in the chat interface
 */

import React, { useRef, useEffect } from 'react';
import './ChatInput.css';

const ChatInput = ({ onSend, loading, disabled }) => {
  const inputRef = useRef(null);

  useEffect(() => {
    if (!loading && !disabled && inputRef.current) {
      inputRef.current.focus();
    }
  }, [loading, disabled]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const input = inputRef.current;
    if (input && input.value.trim()) {
      onSend(input.value);
      input.value = '';
    }
  };

  return (
    <form className="chat-input-container" onSubmit={handleSubmit}>
      <input
        ref={inputRef}
        type="text"
        className="chat-input"
        placeholder="Type your message..."
        disabled={loading || disabled}
      />
      <button 
        type="submit" 
        className="send-button"
        disabled={loading || disabled}
      >
        {loading ? 'Sending...' : 'Send'}
      </button>
    </form>
  );
};

export default ChatInput; 