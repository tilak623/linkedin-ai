import React, { useEffect, useRef, useState } from 'react';
import { AlertCircle, CheckCircle2, Mic, MicOff, Send, Sparkles } from 'lucide-react';
import { api } from '../services/api';
import { InterviewMode, InterviewSession, InterviewTurnResult } from '../types';

interface SpeechRecognitionResultLike {
  0: { transcript: string };
}

interface SpeechRecognitionEventLike {
  results: ArrayLike<SpeechRecognitionResultLike>;
}

interface SpeechRecognitionInstance {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((event: SpeechRecognitionEventLike) => void) | null;
  onerror: (() => void) | null;
  onend: (() => void) | null;
  start: () => void;
  stop: () => void;
}

interface SpeechRecognitionWindow extends Window {
  SpeechRecognition?: new () => SpeechRecognitionInstance;
  webkitSpeechRecognition?: new () => SpeechRecognitionInstance;
}

const opportunityLabels: Record<InterviewTurnResult['content_opportunity'], string> = {
  technical_educational_post: 'Possible technical educational post',
  learning_experience: 'Possible learning experience',
  project_update: 'Possible project update',
  technical_opinion: 'Possible technical opinion',
  none: 'No post suggested; this is fine',
};

export const Interview: React.FC = () => {
  const [session, setSession] = useState<InterviewSession | null>(null);
  const [mode, setMode] = useState<InterviewMode>('text');
  const [inputText, setInputText] = useState('');
  const [contentOpportunity, setContentOpportunity] = useState<InterviewTurnResult['content_opportunity'] | null>(null);
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [error, setError] = useState('');
  const recognitionRef = useRef<SpeechRecognitionInstance | null>(null);

  useEffect(() => {
    let active = true;
    const loadToday = async () => {
      const result = await api.getTodayInterview();
      if (!active) return;
      if (!result.success) {
        setError(result.error?.message ?? 'Could not load today’s interview.');
      } else if (result.data) {
        setSession(result.data);
        setMode(result.data.mode);
      }
      setLoading(false);
    };
    void loadToday();
    return () => {
      active = false;
      recognitionRef.current?.stop();
    };
  }, []);

  const startInterview = async () => {
    setBusy(true);
    setError('');
    const result = await api.startInterview(mode);
    setBusy(false);
    if (!result.success || !result.data) {
      setError(result.error?.message ?? 'Could not start the interview.');
      return;
    }
    setSession(result.data);
  };

  const sendAnswer = async (event?: React.FormEvent) => {
    event?.preventDefault();
    const answer = inputText.trim();
    if (!session || session.completed || !answer || busy) return;
    setBusy(true);
    setError('');
    const result = await api.submitInterviewTurn(session.id, answer);
    setBusy(false);
    if (!result.success || !result.data) {
      setError(result.error?.message ?? 'Your answer could not be saved. It remains in the input so you can retry.');
      return;
    }
    setSession(result.data.session);
    setContentOpportunity(result.data.content_opportunity);
    setInputText('');
  };

  const finishInterview = async () => {
    if (!session || session.completed || busy) return;
    setBusy(true);
    setError('');
    const result = await api.completeInterview(session.id);
    setBusy(false);
    if (!result.success || !result.data) {
      setError(result.error?.message ?? 'Could not finish the interview.');
      return;
    }
    setSession(result.data);
    setContentOpportunity(null);
  };

  const toggleRecording = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
      setIsRecording(false);
      return;
    }
    const speechWindow = window as SpeechRecognitionWindow;
    const Recognition = speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition;
    if (!Recognition) {
      setError('Voice recognition is unavailable in this browser. You can continue by typing.');
      return;
    }
    const recognition = new Recognition();
    recognition.lang = 'en-US';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.onresult = (event) => {
      const transcript = event.results[0]?.[0]?.transcript;
      if (transcript) setInputText((current) => current ? `${current} ${transcript}` : transcript);
    };
    recognition.onerror = () => {
      setIsRecording(false);
      recognitionRef.current = null;
      setError('Voice recognition failed. Your typed input is still available.');
    };
    recognition.onend = () => {
      setIsRecording(false);
      recognitionRef.current = null;
    };
    recognitionRef.current = recognition;
    setError('');
    setIsRecording(true);
    try {
      recognition.start();
    } catch {
      recognitionRef.current = null;
      setIsRecording(false);
      setError('Could not start voice recognition. You can continue by typing.');
    }
  };

  if (loading) {
    return <p className="text-sm text-slate-400">Loading today’s interview…</p>;
  }

  return (
    <div className="mx-auto flex h-[calc(100vh-8.5rem)] max-w-4xl flex-col space-y-4">
      <div className="flex items-start gap-2 rounded-xl border border-brand-500/20 bg-brand-950/20 p-3.5 text-xs text-brand-200">
        <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-brand-400" />
        <p>
          The guided interviewer saves each turn locally and chooses follow-ups from your answers. No external AI provider is called in this phase; use text if you don’t want your browser’s speech service to process audio.
        </p>
      </div>

      {!session && (
        <section className="rounded-xl border border-surface-800 bg-surface-900 p-6">
          <h2 className="text-base font-semibold text-slate-100">Start today’s reflection</h2>
          <p className="mt-2 text-sm text-slate-400">Share a project update, something you learned, a problem you solved, or simply say there was no major progress. You can finish whenever you like.</p>
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <label className="text-xs text-slate-300" htmlFor="interview-mode">Input mode</label>
            <select id="interview-mode" value={mode} onChange={(e) => setMode(e.target.value as InterviewMode)} className="rounded-lg border border-surface-700 bg-surface-950 px-3 py-2 text-sm text-slate-100">
              <option value="text">Text</option>
              <option value="voice">Voice input</option>
            </select>
            <button disabled={busy} onClick={() => void startInterview()} className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-500 disabled:opacity-50">
              {busy ? 'Starting…' : 'Start interview'}
            </button>
          </div>
        </section>
      )}

      {session && (
        <>
          <div className="flex items-center justify-between rounded-xl border border-surface-800 bg-surface-900 px-4 py-3 text-xs">
            <div className="text-slate-300">Today · {session.mode === 'voice' ? 'Voice input' : 'Text'} · {session.messages.filter((message) => message.sender === 'user').length} answers</div>
            {session.completed ? (
              <span className="inline-flex items-center gap-1 text-emerald-300"><CheckCircle2 className="h-4 w-4" /> Complete</span>
            ) : (
              <button onClick={() => void finishInterview()} disabled={busy || Boolean(inputText.trim())} title={inputText.trim() ? 'Send or clear your unsaved answer first' : 'Finish the interview'} className="text-slate-400 underline hover:text-slate-100 disabled:opacity-50">Finish now</button>
            )}
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto rounded-xl border border-surface-800 bg-surface-900 p-4">
            {session.messages.map((message) => (
              <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <article className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${message.sender === 'ai' ? 'border border-surface-700/50 bg-surface-800 text-slate-100' : 'bg-brand-600 text-white'}`}>
                  <p className="whitespace-pre-wrap">{message.content}</p>
                  <time className="mt-1 block text-[10px] opacity-70">{new Date(message.created_at).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' })}</time>
                </article>
              </div>
            ))}
            {busy && <p className="text-xs text-slate-500">Saving your answer…</p>}
          </div>

          {session.completed && (
            <div className="rounded-xl border border-emerald-800/50 bg-emerald-950/20 p-4">
              <h3 className="text-sm font-semibold text-emerald-200">Reflection saved</h3>
              {contentOpportunity && <p className="mt-1 text-xs text-emerald-100/80">{opportunityLabels[contentOpportunity]}</p>}
              <p className="mt-2 whitespace-pre-wrap text-xs text-slate-300">{session.summary || 'No answer was recorded.'}</p>
            </div>
          )}

          {!session.completed && (
            <form onSubmit={(event) => void sendAnswer(event)} className="rounded-xl border border-surface-800 bg-surface-900 p-3">
              <div className="flex items-center gap-2">
                {session.mode === 'voice' && (
                  <button type="button" onClick={toggleRecording} aria-label={isRecording ? 'Stop voice input' : 'Start voice input'} className={`rounded-xl p-3 ${isRecording ? 'bg-rose-600 text-white' : 'bg-surface-800 text-slate-300 hover:bg-surface-700'}`}>
                    {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                  </button>
                )}
                <input value={inputText} onChange={(e) => setInputText(e.target.value)} maxLength={8000} disabled={busy} className="min-w-0 flex-1 rounded-xl border border-surface-800 bg-surface-950 px-4 py-2.5 text-sm text-slate-100 placeholder:text-slate-500 focus:border-brand-500 focus:outline-none" placeholder={isRecording ? 'Listening…' : 'Type your answer…'} />
                <button type="submit" disabled={!inputText.trim() || busy} className="rounded-xl bg-brand-600 p-3 text-white hover:bg-brand-500 disabled:opacity-40"><Send className="h-4 w-4" /></button>
              </div>
              {error && <p role="alert" className="mt-2 flex items-center gap-1.5 text-xs text-rose-300"><AlertCircle className="h-3.5 w-3.5" />{error}</p>}
            </form>
          )}
        </>
      )}

      {!session && error && <p role="alert" className="flex items-center gap-1.5 text-sm text-rose-300"><AlertCircle className="h-4 w-4" />{error}</p>}
    </div>
  );
};
