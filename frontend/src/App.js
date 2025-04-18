// src/App.js
import React, { useState } from 'react';
import './App.css';
import TextToSpeechComponent from './components/TextToSpeechComponent';
import ChatbotComponent from './components/ChatbotComponent';

function App() {
  const [activeTab, setActiveTab] = useState('tts');

  return (
    <div className="app-container">
      <header>
        <h1>GROQ Speech & Chat Demo</h1>
        <p>Explore text-to-speech and conversational AI powered by GROQ</p>
        
        <div className="tabs">
          <button 
            className={`tab-button ${activeTab === 'tts' ? 'active' : ''}`}
            onClick={() => setActiveTab('tts')}
          >
            Text-to-Speech-to-Text
          </button>
          <button 
            className={`tab-button ${activeTab === 'chatbot' ? 'active' : ''}`}
            onClick={() => setActiveTab('chatbot')}
          >
            Chatbot with Voice
          </button>
        </div>
      </header>
      
      <main>
        {activeTab === 'tts' ? (
          <TextToSpeechComponent />
        ) : (
          <ChatbotComponent />
        )}
      </main>
    </div>
  );
}

export default App;