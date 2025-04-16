import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import apiClient from '../../utils/apiClient';
import InventoryDisplay from './InventoryDisplay';
import Message from './Message';
import ChatInput from './ChatInput';
import './Chat.css';
import { useNavigate } from 'react-router-dom';

// A simple function to generate a unique ID.
const generateUniqueId = () => {
  return `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
};

// Function to get current time in EST
const getCurrentTimeInEST = () => {
  try {
    const now = new Date();
    const options = { 
      timeZone: 'America/New_York',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    };
    
    const estDate = new Intl.DateTimeFormat('en-US', options).format(now);
    const [datePart, timePart] = estDate.split(', ');
    const [month, day, year] = datePart.split('/');
    
    return `${year}-${month}-${day} ${timePart} EST`;
  } catch (error) {
    console.error("Error formatting EST time:", error);
    const now = new Date();
    const estOffset = -5; // EST is UTC-5
    const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
    const est = new Date(utc + (3600000 * estOffset));
    
    return est.toISOString().replace('T', ' ').split('.')[0] + ' EST';
  }
};

const TypingIndicator = () => (
  <div className="typing-indicator">
    <span></span>
    <span></span>
    <span></span>
  </div>
);

const Chat = ({ analyticsData, updateAnalytics }) => {
  const [messages, setMessages] = useState([
    { 
      id: generateUniqueId(), 
      sender: 'bot', 
      text: 'Hello! How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [loading, setLoading] = useState(false);
  const [toolCallInProgress, setToolCallInProgress] = useState(false);
  const [conversationHistory, setConversationHistory] = useState([]);
  const [summary, setSummary] = useState(null);
  const [showSummary, setShowSummary] = useState(false);
  const [isSummaryExpanded, setIsSummaryExpanded] = useState(false);
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, summary]);

  useEffect(() => {
    if (summary) {
      const timer = setTimeout(() => {
        setShowSummary(true);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [summary]);

  const handleSend = async (message) => {
    if (!message.trim()) return;

    const userMessage = { 
      id: generateUniqueId(), 
      sender: 'user', 
      text: message,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      let formattedHistory = conversationHistory.length > 0 
        ? [...conversationHistory] 
        : [];
      
      const currentTime = getCurrentTimeInEST();
      
      formattedHistory.push({
        role: "system",
        content: `Current time: ${currentTime}`
      });
      
      formattedHistory.push({
        role: 'user',
        content: message
      });

      const payload = {
        message: message,
        conversation_history: formattedHistory
      };

      const response = await apiClient.post('/chat', payload);
      const { chat_response, conversation_history: updatedHistory, tool_call_detected, summary: newSummary, analytics: updatedAnalytics } = response.data;
      
      setConversationHistory(updatedHistory);

      if (updatedAnalytics) {
        updateAnalytics(updatedAnalytics);
      }

      if (tool_call_detected) {
        setToolCallInProgress(true);
        
        const searchingMessage = { 
          id: generateUniqueId(), 
          sender: 'bot', 
          text: 'Please wait while I search our inventory.',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, searchingMessage]);
        
        const toolCallResponse = await apiClient.post('/tool-call-result', {
          conversation_history: updatedHistory
        });
        
        const { final_response, final_conversation_history, summary: toolCallSummary, analytics: toolCallAnalytics } = toolCallResponse.data;
        
        setConversationHistory(final_conversation_history);
        
        if (toolCallAnalytics) {
          updateAnalytics(toolCallAnalytics);
        }
        
        const finalMessage = { 
          id: generateUniqueId(), 
          sender: 'bot', 
          text: final_response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, finalMessage]);
        
        setToolCallInProgress(false);
        
        if (toolCallSummary) {
          setSummary(toolCallSummary);
          setShowSummary(true);
        }
      } else {
        const botMessage = { 
          id: generateUniqueId(), 
          sender: 'bot', 
          text: chat_response,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, botMessage]);
        
        if (newSummary) {
          setSummary(newSummary);
          setShowSummary(true);
        }
      }
    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = { 
        id: generateUniqueId(), 
        sender: 'bot', 
        text: 'Sorry, I encountered an error. Please try again later.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyticsClick = () => {
    navigate('/analytics');
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h2>Nissan of Hendersonville Chat</h2>
        <div className="header-buttons">
          <InventoryDisplay />
          <button 
            className="analytics-button"
            onClick={handleAnalyticsClick}
          >
            View Analytics
          </button>
        </div>
      </div>
      
      {showSummary && summary && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="summary-container"
        >
          <div 
            className="summary-header"
            onClick={() => setIsSummaryExpanded(!isSummaryExpanded)}
          >
            <h3>Conversation Summary</h3>
            <div className={`dropdown-arrow ${isSummaryExpanded ? 'expanded' : ''}`}>
              <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M2 4L6 8L10 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
          </div>
          
          {isSummaryExpanded && (
            <div className="summary-content">
              <div className="summary-section">
                <h4>Sentiment</h4>
                <p className={`sentiment ${summary.sentiment}`}>{summary.sentiment}</p>
              </div>
              
              <div className="summary-section">
                <h4>Keywords</h4>
                <div className="keywords">
                  {summary.keywords.map((keyword, index) => (
                    <span key={index} className="keyword-tag">{keyword}</span>
                  ))}
                </div>
              </div>
              
              <div className="summary-section">
                <h4>Summary</h4>
                <p>{summary.summary}</p>
              </div>
              
              <div className="summary-section">
                <h4>Recommended Department</h4>
                <p className="department">{summary.department}</p>
              </div>
              
              <div className="summary-section">
                <h4>Additional Insights</h4>
                <ul>
                  <li><strong>Urgency:</strong> {summary.insights.urgency}</li>
                  <li><strong>Upsell Opportunity:</strong> {summary.insights.upsell_opportunity ? 'Yes' : 'No'}</li>
                  <li><strong>Customer Interest:</strong> {summary.insights.customer_interest}</li>
                  {summary.insights.additional_notes && (
                    <li><strong>Notes:</strong> {summary.insights.additional_notes}</li>
                  )}
                </ul>
              </div>
            </div>
          )}
        </motion.div>
      )}
      
      <div className="chat-messages">
        <AnimatePresence>
          {messages.map((message) => (
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              <Message message={message} />
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>
      
      <ChatInput 
        onSend={handleSend}
        loading={loading}
        disabled={toolCallInProgress}
      />
    </div>
  );
};

export default Chat;
