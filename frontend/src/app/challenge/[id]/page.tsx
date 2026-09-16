'use client';

import { useEffect, useState, use } from 'react';
import Link from 'next/link';
import { api } from '../../../lib/api';
import { mergeSort, type Direction } from '../../../lib/mergeSort';
import type { Challenge, Submission, RankedRow, RevealResponse } from '../../../lib/types';
import { Badge, EmptyState, Flash, type FlashMessage } from '../../../components/ui';

const COLUMNS: { key: keyof RankedRow; label: string; help: string }[] = [
  { key: 'relevance', label: 'Relevance', help: 'Does it answer what was asked' },
  { key: 'quality', label: 'Quality', help: 'How closely it matches the brief' },
  { key: 'structure', label: 'Structure', help: 'Does it contain real working logic' },
  { key: 'plagiarism', label: 'Copied', help: 'How much also appears in another entry' },
  { key: 'final_score', label: 'Score', help: 'The four above, combined' },
];

export default function ChallengePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const challengeId = Number(id);

  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [subs, setSubs] = useState<Submission[]>([]);
  const [rows, setRows] = useState<RankedRow[]>([]);
  const [reveal, setReveal] = useState<RevealResponse | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);
  const [busy, setBusy] = useState(false);
  const [showSubmit, setShowSubmit] = useState(false);

  const [sortKey, setSortKey] = useState<keyof RankedRow>('final_score');
  const [direction, setDirection] = useState<Direction>('desc');

  const [content, setContent] = useState('');
  const [name, setName] = useState('');

  const closed = challenge?.revealed ?? false;

  async function load() {
    try {
      const c = await api.challenge(challengeId);
      setChallenge(c);
      setSubs(await api.submissions(challengeId));
      // A finished challenge shows its result straight away, so nobody has to
      // press Rank to see something that has already been decided.
      if (c.revealed) setRows(await api.results(challengeId));
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [challengeId]);

  async function submit() {
    if (!content.trim() || !name.trim()) {
      setFlash({ text: 'Add your work and your name.', err: true });
      return;
    }
    try {
      const res = await api.submit(challengeId, content, name);
      setContent('');
      setName('');
      setShowSubmit(false);
      setFlash({ text: `Submitted as ${res.ghost_id}. The company only sees your work.` });
      load();
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  async function runRank() {
    setBusy(true);
    try {
      const res = await api.rank(challengeId);
      setRows(res.results);
      setReveal(null);
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    } finally {
      setBusy(false);
    }
  }

  async function runReveal() {
    try {
      setReveal(await api.reveal(challengeId));
      load();
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  function sortBy(key: keyof RankedRow) {
    const next: Direction = key === sortKey && direction === 'desc' ? 'asc' : 'desc';
    setSortKey(key);
    setDirection(next);
    setRows(mergeSort(rows, r => r[key] as number, next));
  }

  if (!challenge) {
    return (
      <div className="page">
        <Flash message={flash} />
        <div className="card"><EmptyState title="Loading" /></div>
      </div>
    );
  }

  return (
    <div className="page">
      <Link href="/" className="back-link">← All challenges</Link>

      <section className="card">
        <div className="row-between">
          <div>
            <h1 className="page-title">{challenge.title}</h1>
            <div className="card-meta">{challenge.company} · closes day {challenge.end_day}</div>
          </div>
          <div className="cluster">
            {challenge.reward && <Badge tone="accent">{challenge.reward}</Badge>}
            {closed && <Badge tone="good">Winner announced</Badge>}
          </div>
        </div>
        <p className="card-body">{challenge.statement}</p>

        {/* A closed challenge takes no more entries, so it offers no buttons. */}
        {!closed && (
          <div className="actions">
            <button className="btn" onClick={() => setShowSubmit(!showSubmit)}>
              {showSubmit ? 'Cancel' : 'Submit your work'}
            </button>
            <button className="btn btn-accent" onClick={runRank} disabled={busy || subs.length === 0}>
              {busy ? 'Ranking…' : 'Rank submissions'}
            </button>
          </div>
        )}
      </section>

      <Flash message={flash} />

      {showSubmit && !closed && (
        <section className="card">
          <div className="card-title">Your submission</div>
          <div className="card-meta">No name, no CV, no photo. Only the work is judged.</div>
          <div className="field">
            <label className="field-label">Your work</label>
            <textarea className="field-textarea" rows={7} value={content}
              placeholder="Paste your code or your answer"
              onChange={e => setContent(e.target.value)} />
          </div>
          <div className="field">
            <label className="field-label">Your name</label>
            <input className="field-input" value={name} onChange={e => setName(e.target.value)} />
            <div className="field-hint">Kept private unless you win.</div>
          </div>
          <div className="actions">
            <button className="btn btn-accent" onClick={submit}>Submit</button>
          </div>
        </section>
      )}

      {reveal && (
        <section className="winner">
          <span className="algo-tag">Winner</span>
          <div className="winner-name">{reveal.real_name}</div>
          <div className="winner-score">
            Entered as {reveal.winner.ghost_id} · score {reveal.winner.final_score.toFixed(2)}
          </div>
        </section>
      )}

      {rows.length > 0 && (
        <section className="card">
          <div className="row-between">
            <div>
              <div className="card-title">Results</div>
              <div className="card-meta">
                Every entry judged on the work alone. Click a column to sort.
              </div>
            </div>
            {/* Stays available after the announcement too, so anyone arriving
                later can still see who won. */}
            {!reveal && (
              <button className="btn btn-accent" onClick={runReveal}>Reveal the winner</button>
            )}
          </div>

          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th className="num">#</th>
                  <th>Entry</th>
                  {COLUMNS.map(c => (
                    <th key={c.key} className="num sortable" title={c.help}
                      onClick={() => sortBy(c.key)}>
                      {c.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.ghost_id}>
                    <td className="num">{r.rank}</td>
                    <td style={{ fontFamily: 'var(--mono)', fontSize: 12 }}>{r.ghost_id}</td>
                    <td className="num">{pct(r.relevance)}</td>
                    <td className="num">{pct(r.quality)}</td>
                    <td className="num">{pct(r.structure)}</td>
                    <td className="num">
                      <Badge tone={r.plagiarism > 0.4 ? 'bad' : 'neutral'}>{pct(r.plagiarism)}</Badge>
                    </td>
                    <td className="num"><strong>{r.final_score.toFixed(2)}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="legend-notes">
            {COLUMNS.slice(0, 4).map(c => (
              <div key={c.key}><strong>{c.label}</strong> {c.help}</div>
            ))}
          </div>
        </section>
      )}

      <section className="card">
        <div className="card-title">Entries ({subs.length})</div>
        {subs.length === 0 ? (
          <EmptyState title="Nothing submitted yet" description="Be the first." />
        ) : (
          <div className="stack" style={{ marginTop: 10 }}>
            {subs.map(s => (
              <div key={s.id}>
                <span className="algo-tag">{s.ghost_id}</span>
                <div className="code-block">{s.content}</div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function pct(v: number) {
  return Math.round(v * 100) + '%';
}
