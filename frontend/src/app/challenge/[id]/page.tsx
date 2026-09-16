'use client';

/**
 * The main screen of the demo.
 * Submit anonymously, press Rank, watch every algorithm produce a column,
 * then reveal the winner and the proof that the win is real.
 */

import { useEffect, useState, use } from 'react';
import Link from 'next/link';
import { api } from '../../../lib/api';
import { mergeSort, type Direction } from '../../../lib/mergeSort';
import type {
  Challenge, Submission, RankedRow, RevealResponse,
} from '../../../lib/types';
import { Badge, EmptyState, Flash, type FlashMessage } from '../../../components/ui';

/** Column headers double as a label of which algorithm produced the number. */
const COLUMNS: { key: keyof RankedRow; label: string; algo: string }[] = [
  { key: 'relevance', label: 'Relevance', algo: 'tf idf cosine' },
  { key: 'quality', label: 'Quality', algo: 'levenshtein' },
  { key: 'structure', label: 'Structure', algo: 'cyclomatic' },
  { key: 'plagiarism', label: 'Copied', algo: 'rabin karp' },
  { key: 'final_score', label: 'Final', algo: 'weighted sum' },
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

  const [sortKey, setSortKey] = useState<keyof RankedRow>('final_score');
  const [direction, setDirection] = useState<Direction>('desc');

  const [content, setContent] = useState('');
  const [name, setName] = useState('');

  async function load() {
    try {
      setChallenge(await api.challenge(challengeId));
      setSubs(await api.submissions(challengeId));
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
      setFlash({ text: 'Paste your work and give a name for the reveal.', err: true });
      return;
    }
    try {
      const res = await api.submit(challengeId, content, name);
      setContent('');
      setName('');
      setFlash({ text: `Submitted as ${res.ghost_id}. The company cannot see your name.` });
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
      setFlash({ text: `Scored ${res.results.length} submissions.` });
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

  /** Member 3. The table is reordered in the browser, not on the server. */
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
        <EmptyState title="Loading" description="Make sure the backend is running on port 8000." />
      </div>
    );
  }

  return (
    <div className="page">
      <Link href="/" className="back-link">back to challenges</Link>

      <div className="row-between">
        <div>
          <h1 className="page-title">{challenge.title}</h1>
          <p className="page-subtitle">{challenge.company}</p>
        </div>
        <div className="cluster">
          {challenge.reward && <Badge tone="accent">{challenge.reward}</Badge>}
          <button className="btn btn-accent" onClick={runRank} disabled={busy}>
            {busy ? 'Scoring' : 'Rank submissions'}
          </button>
        </div>
      </div>

      <Flash message={flash} />

      <section className="card">
        <div className="card-title">Problem statement</div>
        <p style={{ color: 'var(--text-muted)' }}>{challenge.statement}</p>
      </section>

      <section className="card">
        <div className="row-between">
          <div className="card-title">Submit anonymously</div>
          <span className="owner">backend  fastapi</span>
        </div>
        <div className="field">
          <label className="field-label">Your work</label>
          <textarea
            className="field-textarea"
            rows={6}
            value={content}
            onChange={e => setContent(e.target.value)}
            placeholder="Paste code or text here"
          />
        </div>
        <div className="field">
          <label className="field-label">Your real name</label>
          <input
            className="field-input"
            value={name}
            onChange={e => setName(e.target.value)}
          />
          <div className="field-hint">
            Stored but never sent to the company until the winner is revealed.
          </div>
        </div>
        <button className="btn" onClick={submit}>Submit</button>
      </section>

      <section className="card">
        <div className="row-between">
          <div className="card-title">Submissions received ({subs.length})</div>
          <span className="owner">database  postgresql</span>
        </div>
        {subs.length === 0 ? (
          <EmptyState title="Nothing submitted yet" />
        ) : (
          <div className="stack">
            {subs.map(s => (
              <div key={s.id}>
                <span className="algo-tag">{s.ghost_id}</span>
                <div className="code-block">{s.content}</div>
              </div>
            ))}
          </div>
        )}
      </section>

      {rows.length > 0 && (
        <section className="card">
          <div className="row-between">
            <div>
              <div className="card-title">Ranking</div>
              <div className="card-meta">
                Click a header to re sort in the browser with merge sort.
              </div>
            </div>
            <span className="owner">algorithms  nine of them</span>
          </div>

          <div className="table-wrap" style={{ marginTop: '0.75rem' }}>
            <table className="data">
              <thead>
                <tr>
                  <th className="num">#</th>
                  <th>Ghost</th>
                  {COLUMNS.map(c => (
                    <th
                      key={c.key}
                      className="num"
                      style={{ cursor: 'pointer' }}
                      onClick={() => sortBy(c.key)}
                    >
                      {c.label}
                      <span className="algo-tag">{c.algo}</span>
                    </th>
                  ))}
                  <th>Longest copied passage</th>
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.ghost_id}>
                    <td className="num">{r.rank}</td>
                    <td style={{ fontFamily: 'var(--font-mono)' }}>{r.ghost_id}</td>
                    <td className="num">{r.relevance.toFixed(3)}</td>
                    <td className="num">{r.quality.toFixed(3)}</td>
                    <td className="num">
                      {r.structure.toFixed(2)}
                      <span className="algo-tag">paths {r.cyclomatic}</span>
                    </td>
                    <td className="num">
                      <Badge tone={r.plagiarism > 0.4 ? 'bad' : 'neutral'}>
                        {(r.plagiarism * 100).toFixed(0)}%
                      </Badge>
                    </td>
                    <td className="num"><strong>{r.final_score.toFixed(3)}</strong></td>
                    <td>
                      {r.longest_copied ? (
                        <code style={{ fontSize: 11 }}>{r.longest_copied.slice(0, 40)}</code>
                      ) : (
                        <span style={{ color: 'var(--text-faint)' }}>none</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div style={{ marginTop: '1rem' }}>
            <button className="btn btn-accent" onClick={runReveal}>
              Reveal the winner
            </button>
          </div>
        </section>
      )}

      {reveal && (
        <section className="stack">
          <div className="winner">
            <span className="algo-tag">winner of {challenge.title}</span>
            <div className="winner-name">{reveal.real_name}</div>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12, marginTop: 6 }}>
              {reveal.winner.ghost_id} scored {reveal.winner.final_score.toFixed(3)}
            </div>
          </div>

          <div className="card">
            <div className="row-between">
              <div className="card-title">Skill Proof</div>
              <span className="owner">blockchain  merkle tree</span>
            </div>
            <div className="card-meta">
              The win is one leaf in a tree of {reveal.leaf_count}. Anyone can check it
              with the {reveal.proof.length} sibling hashes below, without seeing the
              other submissions.
            </div>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="algo-tag">merkle root</span>
              <div className="hash">{reveal.merkle_root}</div>
            </div>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="algo-tag">leaf</span>
              <div className="hash">{reveal.leaf}</div>
            </div>
            <div style={{ marginTop: '0.75rem' }}>
              <span className="algo-tag">proof path</span>
              {reveal.proof.map((p, i) => (
                <div key={i} className="hash">
                  {p.side} {p.hash}
                </div>
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
