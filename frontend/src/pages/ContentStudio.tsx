import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { AlertCircle, CheckCircle, ExternalLink, ImagePlus, Link2, Loader2, Send, ShieldCheck, Sparkles, Trash2, Unlink } from 'lucide-react';
import { api } from '../services/api';
import { ContentMedia, ContentPost, ContentSchedule, LinkedInStatus } from '../types';

const API_BASE_URL = '/api/v1';

const statusLabel: Record<ContentPost['status'], string> = {
  draft: 'Needs review',
  scheduled: 'Approved & scheduled',
  publishing: 'Publishing',
  published: 'Published',
  publish_failed: 'Publishing failed',
  missed_schedule: 'Missed schedule — review again',
};

export const ContentStudio: React.FC = () => {
  const [posts, setPosts] = useState<ContentPost[]>([]);
  const [linkedin, setLinkedIn] = useState<LinkedInStatus | null>(null);
  const [schedule, setSchedule] = useState<ContentSchedule | null>(null);
  const [media, setMedia] = useState<ContentMedia[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const selectedPost = useMemo(
    () => posts.find((post) => post.id === selectedId) ?? null,
    [posts, selectedId],
  );

  const loadWorkspace = useCallback(async () => {
    const [postResponse, linkedInResponse, scheduleResponse] = await Promise.all([
      api.getContentPosts(),
      api.getLinkedInStatus(),
      api.getContentSchedule(),
    ]);
    if (postResponse.success && postResponse.data) {
      setPosts(postResponse.data);
      setSelectedId((current) => current && postResponse.data?.some((post) => post.id === current)
        ? current
        : postResponse.data?.[0]?.id ?? null);
    } else {
      setError(postResponse.error?.message ?? 'Could not load saved drafts.');
    }
    if (linkedInResponse.success && linkedInResponse.data) {
      setLinkedIn(linkedInResponse.data);
    } else {
      setError(linkedInResponse.error?.message ?? 'Could not load LinkedIn connection status.');
    }
    if (scheduleResponse.success && scheduleResponse.data) {
      setSchedule(scheduleResponse.data);
    } else {
      setError(scheduleResponse.error?.message ?? 'Could not load the posting schedule.');
    }
  }, []);

  useEffect(() => {
    const result = new URLSearchParams(window.location.search).get('linkedin');
    if (result === 'connected') setNotice('LinkedIn connected. Each post still needs your approval.');
    if (result === 'denied') setError('LinkedIn authorization was declined.');
    if (result === 'failed') setError('LinkedIn connection failed. Check the app configuration and try again.');
    if (result) window.history.replaceState({}, '', window.location.pathname);
    void loadWorkspace();
  }, [loadWorkspace]);

  useEffect(() => {
    if (selectedPost) {
      setTitle(selectedPost.title);
      setContent(selectedPost.final_content);
    } else {
      setTitle('');
      setContent('');
    }
  }, [selectedPost]);

  useEffect(() => {
    let active = true;
    setMedia([]);
    if (selectedPost?.id) {
      void api.getPostMedia(selectedPost.id).then((response) => {
        if (!active) return;
        if (response.success && response.data) {
          setMedia(response.data);
        } else {
          setError(response.error?.message ?? 'Could not load post media.');
        }
      });
    }
    return () => {
      active = false;
    };
  }, [selectedPost?.id]);

  const runAction = async (action: () => Promise<{ success: boolean; data: ContentPost | null; error?: { message: string } | undefined }>) => {
    setBusy(true);
    setError('');
    setNotice('');
    const response = await action();
    setBusy(false);
    if (!response.success || !response.data) {
      setError(response.error?.message ?? 'The request could not be completed.');
      return;
    }
    setPosts((current) => [response.data!, ...current.filter((post) => post.id !== response.data!.id)]);
    setSelectedId(response.data.id);
    if (response.data.status === 'scheduled') {
      setNotice(`Approved. It is scheduled for ${new Date(response.data.scheduled_for ?? '').toLocaleString()}.`);
    } else if (response.data.status === 'draft') {
      setNotice('Draft saved.');
    }
  };

  const generateDraft = async () => {
    setBusy(true);
    setError('');
    setNotice('');
    const response = await api.generateContentDraft();
    setBusy(false);
    if (!response.success || !response.data) {
      setError(response.error?.message ?? 'Could not generate a draft.');
      return;
    }
    setPosts((current) => [response.data!, ...current]);
    setSelectedId(response.data.id);
    setNotice('Draft created from saved interview, project, or learning evidence. Review it before approval.');
  };

  const saveDraft = () => {
    if (!selectedPost) return;
    void runAction(() => api.updateContentDraft(selectedPost.id, title, content));
  };

  const uploadMedia = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!selectedPost || !file) return;
    setBusy(true);
    setError('');
    const response = await api.uploadPostMedia(selectedPost.id, file);
    setBusy(false);
    if (!response.success || !response.data) {
      setError(response.error?.message ?? 'Could not upload the image.');
      return;
    }
    setMedia([response.data]);
    setNotice('Image attached to this draft. It will be uploaded to LinkedIn when the approved post is published.');
  };

  const removeMedia = async (assetId: string) => {
    if (!selectedPost) return;
    setBusy(true);
    setError('');
    const response = await api.deletePostMedia(selectedPost.id, assetId);
    setBusy(false);
    if (!response.success) {
      setError(response.error?.message ?? 'Could not remove the image.');
      return;
    }
    setMedia((current) => current.filter((item) => item.id !== assetId));
    setNotice('Image removed from this draft.');
  };

  const approveAndSchedule = () => {
    if (!selectedPost || !window.confirm(
      'This explicitly approves this exact text for public posting on your LinkedIn account. Continue?',
    )) return;
    void runAction(() => api.approveContentPost(selectedPost.id));
  };

  const rescheduleMissed = () => {
    if (!selectedPost || !window.confirm(
      'This post was not published at its missed time. Approve this exact text again for the next daily slot?',
    )) return;
    void runAction(() => api.rescheduleMissedPost(selectedPost.id));
  };

  const disconnect = async () => {
    if (!window.confirm('Disconnect this LinkedIn account? Scheduled posts will no longer publish.')) return;
    setBusy(true);
    const response = await api.disconnectLinkedIn();
    setBusy(false);
    if (!response.success) {
      setError(response.error?.message ?? 'Could not disconnect LinkedIn.');
      return;
    }
    setNotice('LinkedIn disconnected.');
    await loadWorkspace();
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <section className="flex flex-col gap-4 rounded-xl border border-surface-800 bg-surface-900 p-5 md:flex-row md:items-center md:justify-between">
        <div>
          <div className="flex items-center gap-2 text-slate-100">
            <Link2 className="h-4 w-4 text-brand-400" />
            <h2 className="font-semibold">LinkedIn publishing connection</h2>
          </div>
          <p className="mt-1 text-xs text-slate-400">
            Uses LinkedIn OAuth and its official Posts API. Expected profile: <a className="text-brand-300 underline" href={linkedin?.expected_profile_url ?? 'https://linkedin.com/tilakc623'} target="_blank" rel="noreferrer">your provided LinkedIn URL</a>. Confirm the authorized member below is the right account.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {linkedin?.connected ? (
            <>
              <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1.5 text-xs text-emerald-300">
                <CheckCircle className="h-3.5 w-3.5" /> Connected
              </span>
              <span className="text-xs text-slate-400">
                {linkedin.member_name ?? 'Authorized member'}
                {linkedin.expires_at && ` · access expires ${new Date(linkedin.expires_at).toLocaleDateString()}`}
              </span>
              <button onClick={disconnect} disabled={busy} className="flex items-center gap-1.5 rounded-lg border border-surface-700 px-3 py-2 text-xs text-slate-300 hover:bg-surface-800 disabled:opacity-50">
                <Unlink className="h-3.5 w-3.5" /> Disconnect
              </button>
            </>
          ) : (
            <button
              onClick={() => window.location.assign(`${API_BASE_URL}/linkedin/connect`)}
              disabled={!linkedin?.configured || busy}
              className="flex items-center gap-2 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white hover:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <ExternalLink className="h-3.5 w-3.5" />               {linkedin?.configured ? 'Connect LinkedIn' : 'Configure LinkedIn OAuth'}
            </button>
          )}
        </div>
      </section>

      <div className="rounded-xl border border-amber-500/20 bg-amber-950/20 p-4 text-xs leading-relaxed text-amber-200">
        <div className="flex items-start gap-2">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-amber-400" />
          <p>
            Evidence-based drafts use saved work; interview answers can also be rewritten by your configured AI provider. Review and edit every draft. Nothing is published until you explicitly approve it. Approved posts are scheduled for {schedule?.daily_post_time ?? '09:00'} {schedule?.timezone ?? 'Asia/Kolkata'};
            the             server must be running at the scheduled time. Posts more than 15 minutes late are held for your review, not published as catch-up.
          </p>
        </div>
      </div>

      {notice && <p role="status" className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">{notice}</p>}
      {error && <p role="alert" className="flex items-center gap-2 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-300"><AlertCircle className="h-4 w-4" />{error}</p>}

      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Saved posts</h3>
            <button onClick={generateDraft} disabled={busy} className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-3 py-2 text-xs font-semibold text-white hover:bg-brand-500 disabled:opacity-50">
              {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
              Generate draft
            </button>
          </div>
          {posts.length === 0 && <p className="rounded-xl border border-surface-800 bg-surface-900 p-4 text-sm text-slate-400">No posts yet. Complete an interview or add evidence to a project or learning milestone, then generate a draft.</p>}
          {posts.map((post) => (
            <button
              key={post.id}
              onClick={() => setSelectedId(post.id)}
              className={`w-full rounded-xl border p-4 text-left transition-colors ${selectedId === post.id ? 'border-brand-500/40 bg-surface-800' : 'border-surface-800 bg-surface-900 hover:bg-surface-800/60'}`}
            >
              <span className={`mb-2 inline-flex rounded px-2 py-1 text-[10px] ${post.status === 'published' ? 'bg-emerald-500/10 text-emerald-300' : post.status === 'publish_failed' ? 'bg-red-500/10 text-red-300' : 'bg-amber-500/10 text-amber-300'}`}>
                {statusLabel[post.status] ?? post.status}
              </span>
              <span className="block line-clamp-2 text-sm font-medium text-slate-100">{post.title}</span>
              {post.scheduled_for && <span className="mt-2 block text-[11px] text-slate-500">{new Date(post.scheduled_for).toLocaleString()}</span>}
            </button>
          ))}
        </section>

        <section className="space-y-4 rounded-xl border border-surface-800 bg-surface-900 p-5">
          {selectedPost ? (
            <>
              <div className="flex flex-wrap items-center justify-between gap-3 border-b border-surface-800 pb-4">
                <div>
                  <h3 className="font-semibold text-slate-100">Review post</h3>
                  <p className="mt-1 text-xs text-slate-400">
                    {selectedPost.status === 'draft' ? 'Edit the draft before approving.' : statusLabel[selectedPost.status] ?? selectedPost.status}
                  </p>
                </div>
                {selectedPost.status === 'published' && selectedPost.linkedin_post_id && (
                  <a href="https://www.linkedin.com/feed/" target="_blank" rel="noreferrer" className="flex items-center gap-1 text-xs text-brand-300 hover:text-brand-200">
                    View LinkedIn feed <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
              <label className="block text-xs font-medium text-slate-300">
                Title
                <input value={title} onChange={(event) => setTitle(event.target.value)} disabled={selectedPost.status !== 'draft'} maxLength={200} className="mt-1.5 w-full rounded-lg border border-surface-700 bg-surface-950 px-3 py-2 text-sm text-slate-100 disabled:opacity-60" />
              </label>
              <label className="block text-xs font-medium text-slate-300">
                LinkedIn post text
                <textarea value={content} onChange={(event) => setContent(event.target.value)} disabled={selectedPost.status !== 'draft'} maxLength={3000} rows={14} className="mt-1.5 w-full resize-y rounded-lg border border-surface-700 bg-surface-950 px-3 py-3 text-sm leading-relaxed text-slate-100 disabled:opacity-60" />
              </label>
              <div className="rounded-lg border border-surface-800 bg-surface-950 p-4">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h4 className="text-xs font-semibold text-slate-200">Proof image</h4>
                    <p className="mt-1 text-[11px] text-slate-500">Attach one JPEG, PNG, or GIF image (up to 10 MB) to publish with this post.</p>
                  </div>
                  {selectedPost.status === 'draft' && media.length === 0 && (
                    <label className="flex cursor-pointer items-center gap-1.5 rounded-lg border border-surface-700 px-3 py-2 text-xs text-slate-200 hover:bg-surface-800">
                      <ImagePlus className="h-3.5 w-3.5" /> Upload image
                      <input type="file" accept="image/jpeg,image/png,image/gif" disabled={busy} onChange={(event) => void uploadMedia(event)} className="sr-only" />
                    </label>
                  )}
                </div>
                {media.map((item) => (
                  <div key={item.id} className="mt-3 flex items-start gap-3">
                    <img src={item.preview_url} alt={`Proof image: ${item.filename}`} className="h-20 w-20 rounded-lg border border-surface-700 object-cover" />
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-xs text-slate-200">{item.filename}</p>
                      <p className="mt-1 text-[11px] text-slate-500">Attached to this post</p>
                    </div>
                    {selectedPost.status === 'draft' && (
                      <button type="button" onClick={() => void removeMedia(item.id)} disabled={busy} aria-label={`Remove ${item.filename}`} className="rounded-lg p-2 text-slate-400 hover:bg-surface-800 hover:text-rose-300 disabled:opacity-50">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
              {selectedPost.status === 'publish_failed' && (
                <p role="alert" className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-xs text-red-300">
                  Publishing did not return a confirmed result. Check your LinkedIn feed before creating or approving another copy to avoid duplicates.
                </p>
              )}
              <div className="flex flex-wrap items-center justify-between gap-3">
                <span className="text-xs text-slate-500">{content.length}/3000 characters</span>
                {selectedPost.status === 'draft' && (
                  <div className="flex gap-2">
                    <button onClick={saveDraft} disabled={busy || !title.trim() || !content.trim()} className="rounded-lg border border-surface-700 px-4 py-2 text-xs font-medium text-slate-200 hover:bg-surface-800 disabled:opacity-50">Save edits</button>
                    <button onClick={approveAndSchedule} disabled={busy || !linkedin?.connected} className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white hover:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-50">
                      <Send className="h-3.5 w-3.5" /> Approve &amp; schedule
                    </button>
                  </div>
                )}
                {selectedPost.status === 'missed_schedule' && (
                  <button onClick={rescheduleMissed} disabled={busy || !linkedin?.connected} className="flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-2 text-xs font-semibold text-white hover:bg-brand-500 disabled:cursor-not-allowed disabled:opacity-50">
                    <Send className="h-3.5 w-3.5" /> Re-approve &amp; reschedule
                  </button>
                )}
              </div>
            </>
          ) : (
            <div className="flex min-h-64 flex-col items-center justify-center gap-3 text-center text-slate-400">
              <Sparkles className="h-8 w-8 text-slate-600" />
              <p className="text-sm">Generate a draft from your saved professional evidence.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};
