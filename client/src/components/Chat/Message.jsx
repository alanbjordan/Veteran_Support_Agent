import React from 'react';
import ReactMarkdown from 'react-markdown';
import { format } from 'date-fns';
import './Message.css';

const Message = ({ message }) => {
  const { sender, text, timestamp } = message;
  const isBot = sender === 'bot';

  return (
    <div className={`message ${isBot ? 'bot' : 'user'}`}>
      <div className="message-content">
        <ReactMarkdown>{text}</ReactMarkdown>
        <div className="message-timestamp">
          {format(new Date(timestamp), 'HH:mm:ss')}
        </div>
      </div>
    </div>
  );
};

export default Message; 