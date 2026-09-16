'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../lib/api';
import type { Challenge } from '../lib/types';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../components/ui';

const BLANK = { title: '', company: '', statement: '', reward: '', start_day: 0, end_day: 7 };

export default function ChallengesPage() {
  const [rows, setRows] = useState<Challenge[] | null>(null);
  const [form, setForm] = useState(BLANK);
  const [open, setOpen] = useState(false);
  const [flash, setFlash] = useState<FlashMessage>(null);

  async function load() {
    try {
      setRows(await api.challenges());
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
      setRows([]);
    }
  }

  useEffect(() => { load(); }, []);

  async function post() {
    if (!form.title.trim() || !form.statement.trim()) {
      setFlash({ text: 'Add a title and describe the problem.', err: true });
      return;
    }
    try {
      await api.createChallenge(form);
      setForm(BLANK);
      setOpen(false);
      setFlash({ text: 'Your challenge is live.' });
      load();
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  return (
    <div className="page">
      <section className="card">
        {!open ? (
          <div className="row-between">
            <div>
              <div className="card-title">Hiring?</div>
              <div className="card-meta">Post a real problem instead of a job advert.</div>
            </div>
            <button className="btn btn-accent" onClick={() => setOpen(true)}>Post a challenge</button>
          </div>
        ) : (
          <>
            <div className="card-title">New challenge</div>
            <div className="field">
              <label className="field-label">Title</label>
              <input className="field-input" value={form.title}
                onChange={e => setForm({ ...form, title: e.target.value })} />
            </div>
            <div className="field">
              <label className="field-label">Company</label>
              <input className="field-input" value={form.company}
                onChange={e => setForm({ ...form, company: e.target.value })} />
            </div>
            <div className="field">
              <label className="field-label">The problem</label>
              <textarea className="field-textarea" rows={4} value={form.statement}
                style={{ fontFamily: 'inherit' }}
                onChange={e => setForm({ ...form, statement: e.target.value })} />
              <div className="field-hint">Be specific. Answers are judged against this.</div>
            </div>
            <div className="field">
              <label className="field-label">Reward</label>
              <input className="field-input" value={form.reward} placeholder="Interview, job offer, cash"
                onChange={e => setForm({ ...form, reward: e.target.value })} />
            </div>
            <div className="cluster">
              <div className="field" style={{ flex: 1 }}>
                <label className="field-label">Opens on day</label>
                <input className="field-input" type="number" value={form.start_day}
                  onChange={e => setForm({ ...form, start_day: Number(e.target.value) })} />
              </div>
              <div className="field" style={{ flex: 1 }}>
                <label className="field-label">Closes on day</label>
                <input className="field-input" type="number" value={form.end_day}
                  onChange={e => setForm({ ...form, end_day: Number(e.target.value) })} />
              </div>
            </div>
            <div className="actions">
              <button className="btn btn-ghost" onClick={() => setOpen(false)}>Cancel</button>
              <button className="btn btn-accent" onClick={post}>Post</button>
            </div>
          </>
        )}
      </section>

      <Flash message={flash} />

      {rows === null && <div className="card"><Skeleton rows={3} /></div>}

      {rows !== null && rows.length === 0 && (
        <div className="card">
          <EmptyState title="No challenges yet" description="Post the first one above." />
        </div>
      )}

      {(rows ?? []).map(c => (
        <Link key={c.id} href={`/challenge/${c.id}`} className="card">
          <div className="row-between">
            <div>
              <div className="card-title">{c.title}</div>
              <div className="card-meta">{c.company} · closes day {c.end_day}</div>
            </div>
            <Badge tone={c.revealed ? 'good' : 'neutral'}>
              {c.revealed ? 'Winner announced' : 'Open'}
            </Badge>
          </div>
          <p className="card-body">{c.statement}</p>
          {c.reward && (
            <div style={{ marginTop: 10 }}>
              <Badge tone="accent">{c.reward}</Badge>
            </div>
          )}
        </Link>
      ))}
    </div>
  );
}
