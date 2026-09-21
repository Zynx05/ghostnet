'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import { Flash, type FlashMessage } from '../../components/ui';

const BLANK = { title: '', company: '', statement: '', reward: '', start_day: 0, end_day: 7 };

export default function PostPage() {
  const router = useRouter();
  const [form, setForm] = useState(BLANK);
  const [flash, setFlash] = useState<FlashMessage>(null);
  const [busy, setBusy] = useState(false);

  async function post() {
    if (!form.title.trim() || !form.statement.trim()) {
      setFlash({ text: 'Add a title and describe the problem.', err: true });
      return;
    }
    setBusy(true);
    try {
      const { id } = await api.createChallenge(form);
      router.push(`/challenge/${id}`);
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
      setBusy(false);
    }
  }

  const set = (k: keyof typeof BLANK) => (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) =>
    setForm({ ...form, [k]: k === 'start_day' || k === 'end_day' ? Number(e.target.value) : e.target.value });

  return (
    <div className="page">
      <section className="card">
        <h1 className="page-title">Post a challenge</h1>
        <div className="card-meta">
          Describe a real problem you need solved. People answer it without names.
          You rank the answers, then reveal the winner.
        </div>

        <Flash message={flash} />

        <div className="field">
          <label className="field-label">Title</label>
          <input className="field-input" value={form.title} onChange={set('title')}
            placeholder="Fix the checkout bug" />
        </div>
        <div className="field">
          <label className="field-label">Company</label>
          <input className="field-input" value={form.company} onChange={set('company')} />
        </div>
        <div className="field">
          <label className="field-label">The problem</label>
          <textarea className="field-textarea" rows={5} value={form.statement}
            style={{ fontFamily: 'inherit' }} onChange={set('statement')} />
          <div className="field-hint">Be specific. Every answer is judged against this text.</div>
        </div>
        <div className="field">
          <label className="field-label">Reward</label>
          <input className="field-input" value={form.reward} onChange={set('reward')}
            placeholder="Interview, job offer, cash" />
        </div>
        <div className="cluster">
          <div className="field" style={{ flex: 1 }}>
            <label className="field-label">Opens on day</label>
            <input className="field-input" type="number" value={form.start_day} onChange={set('start_day')} />
          </div>
          <div className="field" style={{ flex: 1 }}>
            <label className="field-label">Closes on day</label>
            <input className="field-input" type="number" value={form.end_day} onChange={set('end_day')} />
          </div>
        </div>
        <div className="actions">
          <button className="btn btn-ghost" onClick={() => router.push('/')}>Cancel</button>
          <button className="btn btn-accent" onClick={post} disabled={busy}>
            {busy ? 'Posting…' : 'Post it'}
          </button>
        </div>
      </section>
    </div>
  );
}
