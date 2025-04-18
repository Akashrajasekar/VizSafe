// src/ChatbotComponent.js
import React, { useState, useRef } from 'react';
import './ChatbotComponent.css';

function ChatbotComponent() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState(null);
  
  const audioPlayerRef = useRef(null);
  const messagesEndRef = useRef(null);
  const currentAudioUrlRef = useRef(null);
  const currentPlayingMessageIdRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Handle sending a message to the chatbot
  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;
    
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInputMessage('');
    setIsProcessing(true);
    setError(null);
    
    try {
      // First, get the chatbot response
      const chatResponse = await fetch('http://localhost:5000/api/chatbot/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          message: inputMessage,
        }),
      });
      
      if (!chatResponse.ok) {
        throw new Error('Failed to get chatbot response');
      }
      
      const chatResult = await chatResponse.json();
      const botMessageContent = chatResult.response;
      
      // Add a temporary bot message
      const botMessageId = Date.now().toString();
      const botMessage = {
        id: botMessageId,
        role: 'assistant',
        content: botMessageContent,
        timestamp: new Date().toISOString(),
        audioUrl: null,
        transcribedText: null,
        isProcessingAudio: true
      };
      
      setMessages(prevMessages => [...prevMessages, botMessage]);
      scrollToBottom();
      
      // Now process the bot message with TTS and transcription
      const ttsResponse = await fetch('http://localhost:5000/api/tst/text-to-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: botMessageContent,
          voice: "Celeste-PlayAI",
          transcribe: true
        }),
      });
      
      if (!ttsResponse.ok) {
        throw new Error('Failed to process speech');
      }
      
      const ttsResult = await ttsResponse.json();
      const audioUrl = `http://localhost:5000/api/tst/audio/${ttsResult.audio_id}`;
      
      // Update the bot message with audio and transcription
      setMessages(prevMessages => 
        prevMessages.map(msg => 
          msg.id === botMessageId 
            ? {
                ...msg,
                audioUrl: audioUrl,
                transcribedText: ttsResult.transcribed_text,
                isProcessingAudio: false
              }
            : msg
        )
      );
      
      // Auto-play the response
      setTimeout(() => {
        playAudio(botMessageId, audioUrl);
      }, 500);
      
    } catch (err) {
      console.error("Error processing message:", err);
      setError(`Error: ${err.message}`);
    } finally {
      setIsProcessing(false);
      scrollToBottom();
    }
  };

  // Play audio for a specific message
  const playAudio = (messageId, audioUrl) => {
    // Stop any currently playing audio
    if (isPlaying && audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current.currentTime = 0;
      
      // Reset the previously playing message
      if (currentPlayingMessageIdRef.current) {
        const prevMessageElem = document.getElementById(`message-${currentPlayingMessageIdRef.current}`);
        if (prevMessageElem) {
          prevMessageElem.classList.remove('is-speaking');
        }
      }
    }
    
    // Set up new audio
    currentAudioUrlRef.current = audioUrl;
    currentPlayingMessageIdRef.current = messageId;
    
    if (audioPlayerRef.current) {
      audioPlayerRef.current.src = audioUrl;
      audioPlayerRef.current.play()
        .then(() => {
          setIsPlaying(true);
          const messageElem = document.getElementById(`message-${messageId}`);
          if (messageElem) {
            messageElem.classList.add('is-speaking');
          }
        })
        .catch(err => {
          console.error("Audio playback error:", err);
          setError("Error playing audio");
        });
    }
  };

  // Handle audio playback end
  const handleAudioEnded = () => {
    setIsPlaying(false);
    if (currentPlayingMessageIdRef.current) {
      const messageElem = document.getElementById(`message-${currentPlayingMessageIdRef.current}`);
      if (messageElem) {
        messageElem.classList.remove('is-speaking');
      }
      currentPlayingMessageIdRef.current = null;
    }
  };

  // Compare original and transcribed text
  const compareTexts = (original, transcribed) => {
    if (!original || !transcribed) return [];
    
    const originalWords = original.toLowerCase().split(/\s+/);
    const transcribedWords = transcribed.toLowerCase().split(/\s+/);
    
    return originalWords.map((word, index) => {
      if (index < transcribedWords.length) {
        return { 
          text: originalWords[index],
          match: originalWords[index] === transcribedWords[index]
        };
      } else {
        return { text: originalWords[index], match: false };
      }
    });
  };

  return (
    <div className="chatbot-container">
      <header className="chatbot-header">
        <h1>GROQ Chatbot with TTS</h1>
        <p>Chat with an AI assistant powered by GROQ - now with voice responses!</p>
      </header>
      
      <div className="chat-area">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="empty-chat-message">
              Send a message to start chatting with the AI assistant
            </div>
          )}
          
          {messages.map((message) => (
            <div 
              key={message.id} 
              id={`message-${message.id}`}
              className={`message ${message.role === 'user' ? 'user-message' : 'bot-message'}`}
            >
              <div className="message-header">
                <span className="message-sender">{message.role === 'user' ? 'You' : 'AI Assistant'}</span>
                <span className="message-time">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
              
              <div className="message-content">{message.content}</div>
              
              {message.role === 'assistant' && (
                <div className="message-actions">
                  {message.isProcessingAudio ? (
                    <div className="processing-indicator">Processing voice...</div>
                  ) : (
                    message.audioUrl && (
                      <button 
                        className="play-audio-button"
                        onClick={() => playAudio(message.id, message.audioUrl)}
                      >
                        {isPlaying && currentPlayingMessageIdRef.current === message.id 
                          ? 'Stop Voice' 
                          : 'Play Voice'}
                      </button>
                    )
                  )}
                </div>
              )}
              
              {message.role === 'assistant' && message.transcribedText && (
                <div className="transcription-box">
                  <h4>Transcription:</h4>
                  <p>{message.transcribedText}</p>
                  
                  {message.content !== message.transcribedText && (
                    <div className="accuracy-analysis">
                      <h5>Accuracy Analysis:</h5>
                      <div className="word-comparison">
                        {compareTexts(message.content, message.transcribedText).map((word, index) => (
                          <span 
                            key={index} 
                            className={word.match ? 'word-match' : 'word-mismatch'}
                          >
                            {word.text + ' '}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          
          <div ref={messagesEndRef} />
        </div>
        
        <div className="input-area">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
            placeholder="Type a message..."
            disabled={isProcessing}
          />
          <button 
            onClick={handleSendMessage} 
            disabled={isProcessing || !inputMessage.trim()}
            className="send-button"
          >
            {isProcessing ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
      
      {error && <div className="error-message">{error}</div>}
      
      <audio 
        ref={audioPlayerRef}
        onEnded={handleAudioEnded}
        onError={(e) => {
          console.error("Audio playback error:", e);
          setError("Error playing audio");
          handleAudioEnded();
        }}
        style={{ display: 'none' }}
      />
    </div>
  );
}

export default ChatbotComponent;