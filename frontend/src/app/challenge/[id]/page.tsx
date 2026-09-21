'use client';

import { useEffect, useState, use } from 'react';
import Link from 'next/link';
import { api, ApiError } from '../../../lib/api';
import { saveSession, useSession } from '../../../lib/auth';
import { mergeSort, type Direction } from '../../../lib/mergeSort';
import type { Challenge, Submission, RankedRow, RevealResponse, Question, Thread } from '../../../lib/types';
import { Badge, EmptyState, Flash, type FlashMessage } from '../../../components/ui';
import { Bubbles, Composer } from '../../../components/Thread';

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
  const session = useSession();

  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [subs, setSubs] = useState<Submission[]>([]);
  const [rows, setRows] = useState<RankedRow[]>([]);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reveal, setReveal] = useState<RevealResponse | null>(null);
  const [names, setNames] = useState<Record<string, string>>({});
  const [threads, setThreads] = useState<Thread[]>([]);
  const [openThread, setOpenThread] = useState<string | null>(null);
  const [justUnmasked, setJustUnmasked] = useState<string | null>(null);
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

  const isCandidate = session?.role === 'candidate';
  const isOwner = !!session && session.role === 'company' && !!challenge
    && challenge.company_id === session.user_id;
  const myId = session?.ghost_id;
  const closed = challenge?.revealed ?? false;
  const entered = !!myId && subs.some(s => s.ghost_id === myId);

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

  // Names this company already paid for come back so nobody is asked to pay twice.
  useEffect(() => {
    if (isOwner && closed) api.unmasks(challengeId).then(setNames).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOwner, closed, challengeId]);

  // Conversations this company already has going on this challenge.
  useEffect(() => {
    if (isOwner) api.challengeThreads(challengeId).then(setThreads).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOwner, challengeId]);

  async function loadThreads(keep?: string) {
    const rows = await api.challengeThreads(challengeId);
    setThreads(rows);
    if (keep) setOpenThread(keep);
  }

  const fail = (e: unknown) => setFlash({ text: (e as Error).message, err: true });

  async function submit() {
    if (!content.trim()) return setFlash({ text: 'Paste your work first.', err: true });
    try {
      const res = await api.submit(challengeId, content);
      setContent(''); setShowSubmit(false);
      setFlash({ text: `Entered as ${res.ghost_name}. The company sees only the work.` });
      load();
    } catch (e) { fail(e); }
  }

  async function runRank() {
    setBusy(true);
    try { setRows((await api.rank(challengeId)).results); setReveal(null); }
    catch (e) { fail(e); }
    finally { setBusy(false); }
  }

  async function runReveal() {
    try { setReveal(await api.reveal(challengeId)); load(); }
    catch (e) { fail(e); }
  }

  async function unmask(ghostId: string) {
    try {
      const u = await api.unmask(challengeId, ghostId);
      if (u.masked) {
        setNames({ ...names, [ghostId]: '' });
        setFlash({ text: 'This candidate chose to stay masked. You were not charged.' });
        return;
      }
      setNames({ ...names, [ghostId]: u.real_name });
      setJustUnmasked(ghostId);
      if (u.balance_pkr !== undefined && session) saveSession({ ...session, balance_pkr: u.balance_pkr });
      setFlash({ text: u.charged_pkr ? `Unmasked. Rs ${u.charged_pkr.toLocaleString()} charged.` : 'Already paid for. No charge.' });
    } catch (e) {
      if (e instanceof ApiError && e.status === 402) {
        setFlash({ text: 'Not enough balance. Add funds on My challenges.', err: true });
      } else fail(e);
    }
  }

  async function ask() {
    if (!question.trim()) return;
    try { await api.ask(challengeId, question); setQuestion(''); setQuestions(await api.questions(challengeId)); }
    catch (e) { fail(e); }
  }

  async function answer(qid: number) {
    if (!answerText.trim()) return;
    try { await api.answer(qid, answerText); setAnswerFor(null); setAnswerText(''); setQuestions(await api.questions(challengeId)); }
    catch (e) { fail(e); }
  }

  async function tap(ghostId: string) {
    try {
      await api.message(challengeId, ghostId, 'tap');
      setFlash({ text: 'Tapped. They will see it in their inbox and decide.' });
      loadThreads(ghostId);
    } catch (e) { fail(e); }
  }

  async function sendInThread(ghostId: string, text: string) {
    try { await api.message(challengeId, ghostId, 'reply', text); await loadThreads(ghostId); }
    catch (e) { fail(e); }
  }

  async function whisper(ghostId: string) {
    if (!whisperText.trim()) return;
    try {
      await api.message(challengeId, ghostId, 'whisper', whisperText);
      setWhisperFor(null); setWhisperText('');
      setFlash({ text: 'Whispered. Only they can read it.' });
      loadThreads(ghostId);
    } catch (e) { fail(e); }
  }

  function sortBy(key: keyof RankedRow) {
    const next: Direction = key === sortKey && direction === 'desc' ? 'asc' : 'desc';
    setSortKey(key); setDirection(next);
    setRows(mergeSort(rows, r => r[key] as number, next));
  }

  if (!challenge) {
    return <div className="page"><Flash message={flash} /><div className="card"><EmptyState title="Loading" /></div></div>;
  }

  const winner = rows.find(r => r.rank === 1) ?? null;

  return (
    <div className="page">
      <Link href={isOwner ? '/company' : '/'} className="back-link">← {isOwner ? 'My challenges' : 'All challenges'}</Link>

      <section className="card">
        <div className="row-between">
          <div>
            <h1 className="page-title">{challenge.title}</h1>
            <div className="card-meta">{challenge.company} · closes day {challenge.end_day} · {subs.length} {subs.length === 1 ? 'entry' : 'entries'}</div>
          </div>
          <div className="cluster">
            {challenge.reward && <Badge tone="accent">{challenge.reward}</Badge>}
            {closed && <Badge tone="good">Closed</Badge>}
            {entered && !closed && <Badge tone="accent">You entered</Badge>}
            {isOwner && <Badge>Yours</Badge>}
          </div>
        </div>
        <p className="card-body">{challenge.statement}</p>

        {/* What you can do depends on who you are. */}
        {!closed && isCandidate && !entered && (
          <div className="actions">
            <button className="btn btn-accent" onClick={() => setShowSubmit(!showSubmit)}>
              {showSubmit ? 'Cancel' : 'Enter this challenge'}
            </button>
          </div>
        )}
        {!closed && isCandidate && entered && (
          <div className="actions"><span className="card-meta">One entry per ghost. Yours is in.</span></div>
        )}
        {!closed && isOwner && (
          <div className="actions">
            <button className="btn btn-accent" onClick={runRank} disabled={busy || subs.length === 0}>
              {busy ? 'Ranking…' : rows.length ? 'Rank again' : 'Rank entries'}
            </button>
          </div>
        )}
        {!closed && session === null && (
          <div className="actions">
            <Link href="/signup" className="btn btn-accent">Sign up to enter</Link>
            <Link href="/login" className="btn btn-ghost">Log in</Link>
          </div>
        )}
        {closed && isCandidate && (
          <div className="actions"><Link href={`/practice/${challenge.id}`} className="btn">Try it as practice</Link></div>
        )}
      </section>

      <Flash message={flash} />

      {showSubmit && isCandidate && !closed && !entered && (
        <section className="card">
          <div className="card-title">Your entry</div>
          <div className="card-meta">No name, no CV, no photo. You enter as {session?.name}.</div>
          <div className="field">
            <textarea className="field-textarea" rows={8} value={content} placeholder="Paste your code or your answer" onChange={e => setContent(e.target.value)} autoFocus />
          </div>
          <div className="actions"><button className="btn btn-accent" onClick={submit}>Submit</button></div>
        </section>
      )}

      {(reveal || (closed && winner)) && winner && (
        <section className="winner">
          <span className="algo-tag">Winner</span>
          <div className={'winner-name' + (justUnmasked === winner.ghost_id ? ' unmasking' : '')}>
            {names[winner.ghost_id] || winner.ghost_name}
          </div>
          <div className="winner-score">
            {names[winner.ghost_id] ? `Entered as ${winner.ghost_name}` : names[winner.ghost_id] === '' ? 'Chose to stay masked' : 'Ghost name'}
            {' · '}score {winner.final_score.toFixed(2)}
          </div>
          {isOwner && names[winner.ghost_id] === undefined && (
            <button className="btn btn-light" style={{ marginTop: 12 }} onClick={() => unmask(winner.ghost_id)}>
              Unmask for Rs 1,500
            </button>
          )}
        </section>
      )}

      {rows.length > 0 && (
        <section className="card">
          <div className="row-between">
            <div>
              <div className="card-title">Results</div>
              <div className="card-meta">Judged on the work alone. Click a column to sort.</div>
            </div>
            {isOwner && !closed && <button className="btn btn-accent" onClick={runReveal}>Close and announce winner</button>}
          </div>

          <div className="table-wrap">
            <table className="data">
              <thead>
                <tr>
                  <th className="num">#</th>
                  <th>Ghost</th>
                  {COLUMNS.map(c => (
                    <th key={c.key} className="num sortable" title={c.help} onClick={() => sortBy(c.key)}>{c.label}</th>
                  ))}
                  {isOwner && <th></th>}
                </tr>
              </thead>
              <tbody>
                {rows.map(r => (
                  <tr key={r.ghost_id} className={r.ghost_id === myId ? 'row-me' : undefined}>
                    <td className="num">{r.rank}</td>
                    <td>
                      {names[r.ghost_id] ? (
                        <span className={justUnmasked === r.ghost_id ? 'unmasking' : ''}>
                          <strong>{names[r.ghost_id]}</strong> <span className="card-meta">({r.ghost_name})</span>
                        </span>
                      ) : r.ghost_name}
                      {r.ghost_id === myId && <span className="you"> you</span>}
                      {names[r.ghost_id] === '' && <span className="card-meta"> · masked</span>}
                    </td>
                    <td className="num">{pct(r.relevance)}</td>
                    <td className="num">{pct(r.quality)}</td>
                    <td className="num">{pct(r.structure)}</td>
                    <td className="num"><Badge tone={r.plagiarism > 0.4 ? 'bad' : 'neutral'}>{pct(r.plagiarism)}</Badge></td>
                    <td className="num"><strong>{r.final_score.toFixed(2)}</strong></td>
                    {isOwner && (
                      <td className="row-actions">
                        <button className="btn btn-sm" onClick={() => tap(r.ghost_id)}>Tap</button>
                        <button className="btn btn-sm btn-ghost" onClick={() => setWhisperFor(whisperFor === r.ghost_id ? null : r.ghost_id)}>Whisper</button>
                        {closed && names[r.ghost_id] === undefined && (
                          <button className="btn btn-sm btn-pay" onClick={() => unmask(r.ghost_id)}>Rs 1,500</button>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {whisperFor && (
            <div className="whisper-box">
              <div className="card-meta">One private line to {rows.find(r => r.ghost_id === whisperFor)?.ghost_name}. Only they see it.</div>
              <div className="field">
                <input className="field-input" value={whisperText} placeholder="Ranked 3rd. Cleanest logic, but no empty case." onChange={e => setWhisperText(e.target.value)} autoFocus />
              </div>
              <div className="actions">
                <button className="btn btn-ghost" onClick={() => setWhisperFor(null)}>Cancel</button>
                <button className="btn btn-accent" onClick={() => whisper(whisperFor)}>Send</button>
              </div>
            </div>
          )}

          <div className="legend-notes">
            {COLUMNS.slice(0, 4).map(c => <div key={c.key}><strong>{c.label}</strong> {c.help}</div>)}
            {isOwner && <div><strong>Tap</strong> asks to talk. <strong>Whisper</strong> sends one line of feedback. <strong>Rs 1,500</strong> shows a real name, once, after the challenge is closed.</div>}
          </div>
        </section>
      )}

      {isOwner && threads.length > 0 && (
        <section className="card">
          <div className="card-title">Conversations ({threads.length})</div>
          <div className="card-meta">Anyone you tapped or whispered to, and what they said back.</div>
          <div className="thread-tabs">
            {threads.map(t => (
              <button
                key={t.ghost_id}
                className={t.ghost_id === (openThread ?? threads[0].ghost_id) ? 'thread-tab on' : 'thread-tab'}
                onClick={() => setOpenThread(t.ghost_id)}
              >
                {t.ghost_name}
                {t.last_sender === 'ghost' && <span className="thread-dot" title="They replied" />}
              </button>
            ))}
          </div>
          {(() => {
            const t = threads.find(x => x.ghost_id === (openThread ?? threads[0].ghost_id));
            if (!t) return null;
            return (
              <>
                <Bubbles thread={t} mine="company" />
                <Composer onSend={text => sendInThread(t.ghost_id, text)} placeholder={`Write to ${t.ghost_name}`} />
              </>
            );
          })()}
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
            ) : isOwner ? (
              answerFor === q.id ? (
                <div className="qa-answer-box">
                  <input className="field-input" value={answerText} placeholder="Your answer" onChange={e => setAnswerText(e.target.value)} autoFocus />
                  <button className="btn btn-sm btn-accent" onClick={() => answer(q.id)}>Answer</button>
                </div>
              ) : <button className="btn btn-sm btn-ghost" onClick={() => setAnswerFor(q.id)}>Answer</button>
            ) : <div className="card-meta" style={{ marginTop: 4 }}>Waiting for {challenge.company}</div>}
          </div>
        ))}
        {isCandidate && (
          <div className="qa-ask">
            <input className="field-input" value={question} placeholder="Does it need to handle Urdu input?" onChange={e => setQuestion(e.target.value)} onKeyDown={e => e.key === 'Enter' && ask()} />
            <button className="btn btn-sm" onClick={ask}>Ask</button>
          </div>
        )}
      </section>

      <section className="card">
        <div className="card-title">Entries ({subs.length})</div>
        {subs.length === 0 ? <EmptyState title="Nothing entered yet" description="Be the first." /> : (
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
