'use client';

/**
 * Challenge list and the form that posts a new one.
 * This is where the demo starts.
 */

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../lib/api';
import type { Challenge } from '../lib/types';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../components/ui';

const BLANK = {
  title: '',
  company: '',
  statement: '',
  reward: '',
  start_day: 0,
  end_day: 7,
};

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

  useEffect(() => {
    load();
  }, []);

  async function post() {
    if (!form.title.trim() || !form.statement.trim()) {
      setFlash({ text: 'A title and a problem statement are both required.', err: true });
      return;
    }
    try {
      await api.createChallenge(form);
      setForm(BLANK);
      setOpen(false);
      setFlash({ text: 'Challenge posted.' });
      load();
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  return (
    <div className="page">
      <div className="row-between">
        <div>
          <h1 className="page-title">Challenges</h1>
          <p className="page-subtitle">
            A company posts a real problem instead of a job advert. Anyone may answer it.
          </p>
        </div>
        <button className="btn btn-accent" onClick={() => setOpen(!open)}>
          {open ? 'Cancel' : 'Post a challenge'}
        </button>
      </div>

      <Flash message={flash} />

      {open && (
        <section className="card" style={{ marginBottom: '1.25rem' }}>
          <div className="card-title">New challenge</div>
          <div className="field">
            <label className="field-label">Title</label>
            <input
              className="field-input"
              value={form.title}
              onChange={e => setForm({ ...form, title: e.target.value })}
            />
          </div>
          <div className="field">
            <label className="field-label">Company</label>
            <input
              className="field-input"
              value={form.company}
              onChange={e => setForm({ ...form, company: e.target.value })}
            />
          </div>
          <div className="field">
            <label className="field-label">Problem statement</label>
            <textarea
              className="field-textarea"
              rows={4}
              value={form.statement}
              onChange={e => setForm({ ...form, statement: e.target.value })}
            />
            <div className="field-hint">
              Every submission is scored against this text, so the wording matters.
            </div>
          </div>
          <div className="field">
            <label className="field-label">Reward</label>
            <input
              className="field-input"
              value={form.reward}
              onChange={e => setForm({ ...form, reward: e.target.value })}
            />
          </div>
          <div className="cluster">
            <div className="field" style={{ flex: 1 }}>
              <label className="field-label">Opens on day</label>
              <input
                className="field-input"
                type="number"
                value={form.start_day}
                onChange={e => setForm({ ...form, start_day: Number(e.target.value) })}
              />
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label className="field-label">Closes on day</label>
              <input
                className="field-input"
                type="number"
                value={form.end_day}
                onChange={e => setForm({ ...form, end_day: Number(e.target.value) })}
              />
            </div>
          </div>
          <button className="btn btn-accent" onClick={post}>Post it</button>
        </section>
      )}

      {rows === null && <Skeleton rows={3} />}

      {rows !== null && rows.length === 0 && (
        <EmptyState
          title="No challenges yet"
          description="Run python seed.py in the backend folder to load the demo data."
        />
      )}

      <div className="stack">
        {(rows ?? []).map(c => (
          <Link key={c.id} href={`/challenge/${c.id}`} className="card">
            <div className="row-between">
              <div>
                <div className="card-title">{c.title}</div>
                <div className="card-meta">{c.company}</div>
              </div>
              <div className="cluster">
                {c.reward && <Badge>{c.reward}</Badge>}
                <Badge tone={c.revealed ? 'good' : 'neutral'}>
                  {c.revealed ? 'winner revealed' : 'anonymous'}
                </Badge>
              </div>
            </div>
            <p style={{ marginTop: '0.6rem', color: 'var(--text-muted)' }}>{c.statement}</p>
            <div className="card-meta" style={{ marginTop: '0.5rem' }}>
              window: day {c.start_day} to day {c.end_day}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
