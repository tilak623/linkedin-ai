import React, { FormEvent, useState } from 'react';
import { LockKeyhole, Sparkles } from 'lucide-react';
import { api } from '../services/api';

interface LoginProps {
  onAuthenticated: () => void;
}

export const Login: React.FC<LoginProps> = ({ onAuthenticated }) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setBusy(true);
    setError('');
    const result = await api.login(password);
    setBusy(false);
    if (!result.success) {
      setError(result.error?.message ?? 'Could not sign in.');
      return;
    }
    onAuthenticated();
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-surface-950 px-4 text-slate-100">
      <form onSubmit={submit} className="w-full max-w-sm rounded-2xl border border-surface-800 bg-surface-900 p-7 shadow-xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-600">
            <Sparkles className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-lg font-semibold">Personal Brand Manager</h1>
            <p className="text-xs text-slate-400">Private workspace</p>
          </div>
        </div>
        <label htmlFor="app-password" className="mb-2 block text-sm font-medium">App password</label>
        <div className="relative">
          <LockKeyhole className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
          <input
            id="app-password"
            autoComplete="current-password"
            type="password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className="w-full rounded-lg border border-surface-700 bg-surface-950 py-2.5 pl-10 pr-3 text-sm outline-none focus:border-brand-500"
          />
        </div>
        {error && <p role="alert" className="mt-3 text-sm text-red-400">{error}</p>}
        <button
          type="submit"
          disabled={busy || !password}
          className="mt-5 w-full rounded-lg bg-brand-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </main>
  );
};
