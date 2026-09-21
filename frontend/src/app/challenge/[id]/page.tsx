'use client';

import { useEffect, useState, use } from 'react';
import Link from 'next/link';
import { api } from '../../../lib/api';
import { ensureGhost, readGhost } from '../../../lib/ghost';
import { mergeSort, type Direction } from '../../../lib/mergeSort';
import type {
  Challenge, Submission, RankedRow, RevealResponse, Question,
} from '../../../lib/types';
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
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reveal, setReveal] = useState<RevealResponse | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);
  const [busy, setBusy] = useState(false);

  const [showSubmit, setShowSubmit] = useState(false);
  const [content, setContent] = useState('');
  const [question, setQuestion] = useState('');
  const [answerFor, setAnswerFor] = useState<number | null>(null);
  const [answerText, setAnswerText] = useState('');
  const [whisperFor, setWhisperFor] = useState<string | null>(null);
  const [whisperText, setWhisperText] = useState('');

  const [sortKey, setSortKey] = useState<keyof RankedRow>('final_score');
  const [direction, setDirection] = useState<Direction>('desc');

  const myId = readGhost()?.ghost_id;
  const closed = challenge?.revealed ?? false;
  const entered = subs.some(s => s.ghost_id === myId);

  async function load() {
    try {
      const c = await api.challenge(challengeId);
      setChallenge(c);
      setSubs(await api.submissions(challengeId));
      setQuestions(await api.questions(challengeId));
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
    if (!content.trim()) {
      setFlash({ text: 'Paste your work first.', err: true });
      return;
    }
    try {
      await ensureGhost();
      const res = await api.submit(challengeId, content);
      setContent('');
      setShowSubmit(false);
      setFlash({ text: `Entered as ${res.ghost_name}. The company sees only the work.` });
      load();
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  async function runRank() {
    setBusy(true);
    try {
      setRows((await api.rank(challengeId)).results);
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

  async function ask() {
    if (!question.trim()) return;
    try {
      await ensureGhost();
      await api.ask(challengeId, question);
      setQuestion('');
      setQuestions(await api.questions(challengeId));
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  async function answer(qid: number) {
    if (!answerText.trim()) return;
    try {
      await api.answer(qid, answerText);
      setAnswerFor(null);
      setAnswerText('');
      setQuestions(await api.questions(challengeId));
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  async function tap(ghostId: string) {
    try {
      await api.message(challengeId, ghostId, 'tap');
      setFlash({ text: 'Tapped. They will see it in their inbox and decide.' });
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  async function whisper(ghostId: string) {
    if (!whisperText.trim()) return;
    try {
      await api.message(challengeId, ghostId, 'whisper', whisperText);
      setWhisperFor(null);
      setWhisperText('');
      setFlash({ text: 'Whispered. Only they can read it.' });
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
            {entered && !closed && <Badge tone="accent">You entered</Badge>}
          </div>
        </div>
        <p className="card-body">{challenge.statement}</p>

        {!closed && (
          <div className="actions">
            {entered ? (
              <span className="card-meta" style={{ marginRight: 'auto', alignSelf: 'center' }}>
                One entry per ghost. Yours is in.
              </span>
            ) : (
              <button className="btn" onClick={() => setShowSubmit(!showSubmit)}>
                {showSubmit ? 'Cancel' : 'Enter this challenge'}
              </button>
            )}
            <button className="btn btn-accent" onClick={runRank} disabled={busy || subs.length === 0}>
              {busy ? 'Ranking…' : 'Rank entries'}
            </button>
          </div>
        )}
        {closed && (
          <div className="actions">
            <Link href={`/practice/${challenge.id}`} className="btn">Try it as practice</Link>
          </div>
        )}
      </section>

      <Flash message={flash} />

      {showSubmit && !closed && !entered && (
        <section className="card">
          <div className="card-title">Your entry</div>
          <div className="card-meta">
            No name, no CV, no photo. You enter as {readGhost()?.name ?? 'your ghost'}.
          </div>
          <div className="field">
            <textarea className="field-textarea" rows={8} value={content}
              placeholder="Paste your code or your answer"
              onChange={e => setContent(e.target.value)} />
          </div>
          <div className="actions">
            <button className="btn btn-accent" onClick={submit}>Submit</button>
          </div>
        </section>
      )}

      {reveal && (
        <section className="winner">
          <span className="algo-tag">Winner</span>
          <div className="winner-name">
            {reveal.masked ? reveal.winner.ghost_name : reveal.real_name}
          </div>
          <div className="winner-score">
            {reveal.masked
              ? 'Chose to stay masked. The win is on their record either way.'
              : `Entered as ${reveal.winner.ghost_name}`}
            {' · '}score {reveal.winner.final_score.toFixed(2)}
          </div>
        </section>
      )}

      {rows.length > 0 && (
        <section className="card">
          <div className="row-between">
            <div>
              <div className="card-title">Results</div>
              <div className="card-meta">Judged on the work alone. Click a column to sort.</div>
            </div>
            {!reveal && (
              <button className="btn btn-accent" onClick={runReveal}>Reveal the winner</button>
            )}
          </div>

          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th className="num">#</th>
                  <th>Ghost</th>
                  {COLUMNS.map(c => (
                    <th key={c.key} className="num sortable" title={c.help} onClick={() => sortBy(c.key)}>
                      {c.label}
                    </th>
                  ))}
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.ghost_id} className={r.ghost_id === myId ? 'row-me' : undefined}>
                    <td className="num">{r.rank}</td>
                    <td>{r.ghost_name}{r.ghost_id === myId && <span className="you"> you</span>}</td>
                    <td className="num">{pct(r.relevance)}</td>
                    <td className="num">{pct(r.quality)}</td>
                    <td className="num">{pct(r.structure)}</td>
                    <td className="num">
                      <Badge tone={r.plagiarism > 0.4 ? 'bad' : 'neutral'}>{pct(r.plagiarism)}</Badge>
                    </td>
                    <td className="num"><strong>{r.final_score.toFixed(2)}</strong></td>
                    <td className="row-actions">
                      <button className="btn btn-sm" onClick={() => tap(r.ghost_id)}>Tap</button>
                      <button className="btn btn-sm btn-ghost"
                        onClick={() => setWhisperFor(whisperFor === r.ghost_id ? null : r.ghost_id)}>
                        Whisper
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {whisperFor && (
            <div className="whisper-box">
              <div className="card-meta">
                One private line to {rows.find(r => r.ghost_id === whisperFor)?.ghost_name}. Only they see it.
              </div>
              <div className="field">
                <input className="field-input" value={whisperText} placeholder="Ranked 3rd. Cleanest logic, but no empty case."
                  onChange={e => setWhisperText(e.target.value)} />
              </div>
              <div className="actions">
                <button className="btn btn-ghost" onClick={() => setWhisperFor(null)}>Cancel</button>
                <button className="btn btn-accent" onClick={() => whisper(whisperFor)}>Send</button>
              </div>
            </div>
          )}

          <div className="legend-notes">
            {COLUMNS.slice(0, 4).map(c => (
              <div key={c.key}><strong>{c.label}</strong> {c.help}</div>
            ))}
            <div><strong>Tap</strong> tells a ghost you would like to talk. <strong>Whisper</strong> sends one line of feedback.</div>
          </div>
        </section>
      )}

      <section className="card">
        <div className="card-title">Questions ({questions.length})</div>
        <div className="card-meta">Ask anything about the brief. Nobody sees your name.</div>
        {questions.map(q => (
          <div key={q.id} className="qa">
            <div className="qa-q"><span className="qa-who">{q.ghost_name}</span> {q.question}</div>
            {q.answer ? (
              <div className="qa-a"><span className="qa-who">{challenge.company}</span> {q.answer}</div>
            ) : answerFor === q.id ? (
              <div className="qa-answer-box">
                <input className="field-input" value={answerText} placeholder="Answer as the company"
                  onChange={e => setAnswerText(e.target.value)} />
                <button className="btn btn-sm btn-accent" onClick={() => answer(q.id)}>Answer</button>
              </div>
            ) : (
              <button className="btn btn-sm btn-ghost" onClick={() => setAnswerFor(q.id)}>Answer as company</button>
            )}
          </div>
        ))}
        <div className="qa-ask">
          <input className="field-input" value={question} placeholder="Does it need to handle Urdu input?"
            onChange={e => setQuestion(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && ask()} />
          <button className="btn btn-sm" onClick={ask}>Ask</button>
        </div>
      </section>

      <section className="card">
        <div className="card-title">Entries ({subs.length})</div>
        {subs.length === 0 ? (
          <EmptyState title="Nothing entered yet" description="Be the first." />
        ) : (
          <div className="stack" style={{ marginTop: 10 }}>
            {subs.map(s => (
              <div key={s.id}>
                <span className="algo-tag">{s.ghost_name}{s.ghost_id === myId ? ' · you' : ''}</span>
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
