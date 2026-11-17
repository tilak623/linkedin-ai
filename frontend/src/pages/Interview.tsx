import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Send, Sparkles, Volume2, MessageSquare, AlertCircle } from 'lucide-react';

interface Message {
  id: string;
  sender: 'ai' | 'user';
  text: string;
  time: string;
}

export const Interview: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: "Hey! Ready for our daily check-in. What was the most interesting technical concept, problem, or project milestone you worked on today?",
      time: 'Just now',
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [speechSupported, setSpeechSupported] = useState(true);

  useEffect(() => {
    // Check Web Speech API availability
    const SpeechRecognition = (window as unknown as { SpeechRecognition?: unknown; webkitSpeechRecognition?: unknown }).SpeechRecognition ||
      (window as unknown as { webkitSpeechRecognition?: unknown }).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setSpeechSupported(false);
    }
  }, []);

  const handleSend = () => {
    if (!inputText.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: inputText,
      time: 'Just now',
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');

    // Simulate adaptive AI follow-up (will connect to backend endpoint in Phase 3)
    setTimeout(() => {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: "That's a solid engineering challenge. Did you run into any subtle edge cases or performance bottlenecks when implementing that, and what was the key lesson learned?",
        time: 'Just now',
      };
      setMessages((prev) => [...prev, aiResponse]);
    }, 700);
  };

  const toggleRecording = () => {
    if (!speechSupported) {
      alert('Web Speech API is not supported in this browser window. Please use the text input.');
      return;
    }

    if (!isRecording) {
      try {
        const SpeechRecognition = (window as unknown as { SpeechRecognition?: new () => unknown; webkitSpeechRecognition?: new () => unknown }).SpeechRecognition ||
          (window as unknown as { webkitSpeechRecognition?: new () => unknown }).webkitSpeechRecognition;
        if (SpeechRecognition) {
          const recognition = new SpeechRecognition() as {
            continuous: boolean;
            interimResults: boolean;
            lang: string;
            start: () => void;
            stop: () => void;
            onresult: (e: { results: { [key: number]: { [key: number]: { transcript: string } } } }) => void;
            onerror: () => void;
            onend: () => void;
          };
          recognition.continuous = false;
          recognition.interimResults = false;
          recognition.lang = 'en-US';

          recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            setInputText(transcript);
          };

          recognition.onerror = () => setIsRecording(false);
          recognition.onend = () => setIsRecording(false);

          recognition.start();
          setIsRecording(true);
        }
      } catch {
        setIsRecording(false);
      }
    } else {
      setIsRecording(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-4xl mx-auto space-y-4">
      {/* Top Guidance Note */}
      <div className="p-3.5 rounded-xl bg-brand-950/20 border border-brand-500/20 flex items-center justify-between text-xs text-brand-300">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-brand-400 shrink-0" />
          <span>
            The interviewer asks one adaptive question at a time. Speak or type freely — it understands both small daily lessons and major achievements.
          </span>
        </div>
        <span className="font-mono text-[10px] uppercase tracking-wider px-2 py-0.5 rounded bg-brand-500/20 font-semibold">
          Standup Turn 1/3
        </span>
      </div>

      {/* Message History Container */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 rounded-xl bg-surface-900 border border-surface-800">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex items-start gap-3 ${msg.sender === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-xs font-bold ${
                msg.sender === 'ai'
                  ? 'bg-brand-600 text-white shadow-sm shadow-brand-500/20'
                  : 'bg-surface-700 text-slate-200'
              }`}
            >
              {msg.sender === 'ai' ? <Sparkles className="w-4 h-4" /> : 'You'}
            </div>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                msg.sender === 'ai'
                  ? 'bg-surface-800 border border-surface-700/50 text-slate-100'
                  : 'bg-brand-600 text-white shadow-md shadow-brand-600/20'
              }`}
            >
              <p>{msg.text}</p>
              <div
                className={`text-[10px] mt-1.5 flex items-center gap-2 ${
                  msg.sender === 'ai' ? 'text-slate-400' : 'text-brand-200'
                }`}
              >
                <span>{msg.time}</span>
                {msg.sender === 'ai' && (
                  <button className="hover:text-slate-200 transition-colors" title="Listen">
                    <Volume2 className="w-3 h-3" />
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Input & Controls Dock */}
      <div className="p-3 rounded-xl bg-surface-900 border border-surface-800 space-y-3">
        <div className="flex items-center gap-2">
          <button
            onClick={toggleRecording}
            className={`p-3 rounded-xl transition-all ${
              isRecording
                ? 'bg-rose-600 text-white animate-pulse shadow-lg shadow-rose-500/30'
                : 'bg-surface-800 hover:bg-surface-700 text-slate-300 border border-slate-700/50'
            }`}
            title={speechSupported ? (isRecording ? 'Stop Recording' : 'Start Voice Input') : 'Speech not supported'}
          >
            {isRecording ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={isRecording ? 'Listening to your voice...' : 'Type your answer, or use voice...'}
            className="flex-1 bg-surface-950 border border-surface-800 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
          />

          <button
            onClick={handleSend}
            disabled={!inputText.trim()}
            className="p-3 rounded-xl bg-brand-600 hover:bg-brand-500 disabled:opacity-40 disabled:hover:bg-brand-600 text-white transition-all shadow-sm shadow-brand-500/20"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        <div className="flex items-center justify-between text-[11px] text-slate-500 px-1">
          <span className="flex items-center gap-1.5">
            <MessageSquare className="w-3.5 h-3.5 text-slate-400" />
            <span>Voice & text modes switchable seamlessly</span>
          </span>
          <span className="text-emerald-400">100% Free Browser Speech API</span>
        </div>
      </div>
    </div>
  );
};
