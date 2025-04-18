// src/TextToSpeechComponent.js
import React, { useState, useRef } from 'react';

function TextToSpeechComponent() {
  const [inputText, setInputText] = useState('');
  const [originalText, setOriginalText] = useState('');
  const [transcribedText, setTranscribedText] = useState('');
  const [audioUrl, setAudioUrl] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState(null);
  const [showTranscription, setShowTranscription] = useState(true);
  const [usedDefaultText, setUsedDefaultText] = useState(false);
  
  const audioPlayerRef = useRef(null);
  const cardRef = useRef(null);

  // Process the text through TTS and transcription
  const processText = async () => {
    setIsProcessing(true);
    setError(null);
    setUsedDefaultText(false);
    
    try {
      const response = await fetch('http://localhost:5000/api/tst/text-to-speech', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: inputText.trim(), // Send empty string if user hasn't entered anything
          voice: "Celeste-PlayAI",
          transcribe: showTranscription
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to process text');
      }
      
      const result = await response.json();
      
      // Set the original text
      setOriginalText(result.original_text);
      
      // Check if default text was used
      if (result.used_default_text) {
        setUsedDefaultText(true);
      }
      
      // Set the transcribed text if available
      if (result.transcribed_text) {
        setTranscribedText(result.transcribed_text);
      } else {
        setTranscribedText('');
      }
      
      // Set up audio URL for playback
      const audioUrl = `http://localhost:5000/api/tst/audio/${result.audio_id}`;
      setAudioUrl(audioUrl);
      
    } catch (err) {
      console.error("Error processing text:", err);
      setError(`Error: ${err.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  // Play/pause the audio
  const toggleAudio = () => {
    if (audioUrl && audioPlayerRef.current) {
      if (isPlaying) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current.currentTime = 0;
        setIsPlaying(false);
        if (cardRef.current) {
          cardRef.current.classList.remove('is-speaking');
        }
      } else {
        audioPlayerRef.current.play();
        setIsPlaying(true);
        if (cardRef.current) {
          cardRef.current.classList.add('is-speaking');
        }
      }
    }
  };

  // Clear all data
  const clearData = () => {
    setInputText('');
    setOriginalText('');
    setTranscribedText('');
    setAudioUrl(null);
    setIsPlaying(false);
    setError(null);
    setUsedDefaultText(false);
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current.currentTime = 0;
    }
    if (cardRef.current) {
      cardRef.current.classList.remove('is-speaking');
    }
  };

  return (
    <div>
      <section className="input-section">
        <h2>Text Input</h2>
        
        <div className="text-input-container">
          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Enter text to convert to speech... (Leave empty to use a random default message)"
            rows={5}
            disabled={isProcessing}
          />
          
          <div className="options-container">
            <label>
              <input
                type="checkbox"
                checked={showTranscription}
                onChange={() => setShowTranscription(!showTranscription)}
                disabled={isProcessing}
              />
              Transcribe generated speech
            </label>
          </div>
          
          <button 
            onClick={processText} 
            className="process-button"
            disabled={isProcessing}
          >
            {isProcessing ? 'Processing...' : 'Convert to Speech'}
          </button>
        </div>
        
        {error && <div className="error-message">{error}</div>}
      </section>
      
      {(originalText || audioUrl) && (
        <section className="output-section" ref={cardRef}>
          <h2>Results</h2>
          
          {usedDefaultText && (
            <div className="notice-message">
              <p>No text was provided, so a default message was used instead.</p>
            </div>
          )}
          
          <div className="original-text-box">
            <h3>Original Text:</h3>
            <p>{originalText}</p>
          </div>
          
          {audioUrl && (
            <div className="audio-box">
              <div className="audio-header">
                <h3>Generated Speech:</h3>
                <button 
                  onClick={toggleAudio}
                  className="play-button"
                >
                  {isPlaying ? 'Stop Audio' : 'Play Audio'}
                </button>
              </div>
              
              <div className="audio-player-container">
                <audio 
                  ref={audioPlayerRef}
                  src={audioUrl} 
                  onEnded={() => {
                    setIsPlaying(false);
                    if (cardRef.current) {
                      cardRef.current.classList.remove('is-speaking');
                    }
                  }}
                  onError={(e) => {
                    console.error("Audio playback error:", e);
                    setError("Error playing audio");
                  }}
                  controls
                />
              </div>
            </div>
          )}
          
          {showTranscription && transcribedText && (
            <div className="transcription-box">
              <h3>Transcribed Text:</h3>
              <p>{transcribedText}</p>
              
              {originalText !== transcribedText && (
                <div className="difference-analysis">
                  <h4>Accuracy Analysis:</h4>
                  <div className="word-comparison">
                    {compareTexts(originalText, transcribedText).map((word, index) => (
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
          
          <button 
            onClick={clearData}
            className="clear-button"
          >
            Clear & Start Over
          </button>
        </section>
      )}
    </div>
  );
}

// Helper function to compare original and transcribed text
function compareTexts(original, transcribed) {
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
}

export default TextToSpeechComponent;