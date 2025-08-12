import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [currentSubject, setCurrentSubject] = useState("default");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize session
  useEffect(() => {
    const initializeSession = async () => {
      try {
        const response = await axios.post(`${API}/sessions`);
        setSessionId(response.data.id);
      } catch (error) {
        console.error("Failed to create session:", error);
      }
    };
    
    initializeSession();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on load
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const getSubjectIcon = (subject) => {
    const icons = {
      photography: "📸",
      film_directing: "🎬",
      mathematics: "📐",
      default: "🧠"
    };
    return icons[subject] || icons.default;
  };

  const getSubjectName = (subject) => {
    const names = {
      photography: "Photography",
      film_directing: "Film & Media Directing", 
      mathematics: "Mathematics",
      default: "General"
    };
    return names[subject] || names.default;
  };

  const getAIModelName = (modelString) => {
    if (modelString.includes('claude')) return "Claude Sonnet 4";
    if (modelString.includes('gpt-4o')) return "GPT-4o";
    if (modelString.includes('gemini')) return "Gemini 2.0";
    return modelString;
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || !sessionId || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setIsLoading(true);

    // Add user message to chat
    const newUserMessage = {
      id: Date.now(),
      type: "user",
      content: userMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: userMessage,
        session_id: sessionId
      });

      const aiMessage = {
        id: response.data.id,
        type: "ai",
        content: response.data.ai_response,
        subject: response.data.subject,
        ai_model_used: response.data.ai_model_used,
        sources: response.data.sources,
        timestamp: new Date(response.data.timestamp)
      };

      setMessages(prev => [...prev, aiMessage]);
      setCurrentSubject(response.data.subject);

    } catch (error) {
      console.error("Error sending message:", error);
      const errorMessage = {
        id: Date.now(),
        type: "error",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple formatting for better readability
    return content.split('\n').map((line, index) => (
      <React.Fragment key={index}>
        {line}
        {index < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  return (
    <div className="app">
      {/* Header */}
      <div className="header">
        <div className="header-content">
          <div className="title-section">
            <h1>📚 StudyGPT</h1>
            <p>Your AI-powered educational assistant for Year 11 & 12</p>
          </div>
          <div className="subject-indicator">
            <span className="subject-badge">
              {getSubjectIcon(currentSubject)} {getSubjectName(currentSubject)}
            </span>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <div className="welcome-content">
                <h2>Welcome to StudyGPT! 🎓</h2>
                <p>I'm here to help you study:</p>
                <div className="subject-list">
                  <div className="subject-item">📸 Photography</div>
                  <div className="subject-item">🎬 Media & Film Directing</div>
                  <div className="subject-item">📐 Mathematics</div>
                </div>
                <p className="welcome-note">
                  I provide factual, unbiased information from trusted university sources.
                  Ask me anything about these subjects at a Year 11-12 level!
                </p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div key={message.id} className={`message ${message.type}`}>
              <div className="message-content">
                {message.type === "user" && (
                  <div className="user-message">
                    <div className="message-avatar">👤</div>
                    <div className="message-text">{formatMessage(message.content)}</div>
                  </div>
                )}

                {message.type === "ai" && (
                  <div className="ai-message">
                    <div className="ai-header">
                      <div className="message-avatar">🤖</div>
                      <div className="ai-info">
                        <span className="ai-model">
                          {getAIModelName(message.ai_model_used)}
                        </span>
                        <span className="subject-tag">
                          {getSubjectIcon(message.subject)} {getSubjectName(message.subject)}
                        </span>
                      </div>
                    </div>
                    <div className="message-text">{formatMessage(message.content)}</div>
                    
                    {message.sources && message.sources.length > 0 && (
                      <div className="sources-section">
                        <h4>📖 University Sources:</h4>
                        <div className="sources-list">
                          {message.sources.map((source, index) => (
                            <div key={index} className="source-item">
                              <a href={source.url} target="_blank" rel="noopener noreferrer">
                                <strong>{source.name}</strong>
                                <span className="department">{source.department}</span>
                              </a>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {message.type === "error" && (
                  <div className="error-message">
                    <div className="message-avatar">⚠️</div>
                    <div className="message-text">{formatMessage(message.content)}</div>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message ai">
              <div className="message-content">
                <div className="ai-message">
                  <div className="message-avatar">🤖</div>
                  <div className="typing-indicator">
                    <div className="typing-dots">
                      <span></span>
                      <span></span>
                      <span></span>
                    </div>
                    <span className="typing-text">Thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-container">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me about Photography, Film Directing, or Mathematics..."
              className="message-input"
              rows="1"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="send-button"
            >
              {isLoading ? "⏳" : "➤"}
            </button>
          </div>
          <div className="input-help">
            Press Enter to send • Shift + Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;