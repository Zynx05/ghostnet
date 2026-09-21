'use client';

import { useEffect, useState, use } from 'react';
import Link from 'next/link';
import { api } from '../../../lib/api';
import type { Challenge, PracticeResult } from '../../../lib/types';
import { RequireRole } from '../../../components/RequireRole';
import { Badge, EmptyState, Flash, type FlashMessage } from '../../../components/ui';

export default function PracticeAttemptPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return <RequireRole role="candidate"><Attempt challengeId={Number(id)} /></RequireRole>;
}

function Attempt({ challengeId }: { challengeId: number }) {
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [content, setContent] = useState('');
  const [result, setResult] = useState<PracticeResult | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.challenge(challengeId).then(setChallenge).catch(e => setFlash({ text: e.message, err: true }));
  }, [challengeId]);

  async function attempt() {
    if (!content.trim()) return setFlash({ text: 'Write something first.', err: true });
    setBusy(true);
    try { setResult(await api.practice(challengeId, content)); setFlash(null); }
    catch (e) { setFlash({ text: (e as Error).message, err: true }); }
    finally { setBusy(false); }
  }

  if (!challenge) return <div className="page"><Flash message={flash} /><div className="card"><EmptyState title="Loading" /></div></div>;

  return (
    <div className="page">
      <Link href="/practice" className="back-link">← Practice</Link>
      <section className="card">
        <div className="row-between">
          <div>
            <h1 className="page-title">{challenge.title.replace(/^Warm up: /, '')}</h1>
            <div className="card-meta">{challenge.practice ? 'Warm up' : challenge.company}</div>
          </div>
          <Badge>Does not count</Badge>
        </div>
        <p className="card-body">{challenge.statement}</p>
      </section>

      <Flash message={flash} />

      {result ? (
        <section className="card result-card">
          <span className="algo-tag">You would have ranked</span>
          <div className="result-rank"><CountUp to={result.would_rank} suffix={ordinal(result.would_rank)} /> <span>of {result.out_of}</span></div>
          <div className="result-scores">
            <div><span className="algo-tag">Relevance</span>{pct(result.scores.relevance)}</div>
            <div><span className="algo-tag">Quality</span>{pct(result.scores.quality)}</div>
            <div><span className="algo-tag">Structure</span>{pct(result.scores.structure)}</div>
            <div><span className="algo-tag">Score</span>{result.scores.final_score.toFixed(2)}</div>
          </div>
          <div className="actions">
            <button className="btn btn-ghost" onClick={() => setResult(null)}>Try again</button>
            {!challenge.practice && <Link href={`/challenge/${challenge.id}`} className="btn">See the real results</Link>}
          </div>
        </section>
      ) : (
        <section className="card">
          <div className="card-title">Your attempt</div>
          <div className="field">
            <textarea className="field-textarea" rows={9} value={content} placeholder="Paste your code or your answer" onChange={e => setContent(e.target.value)} autoFocus />
          </div>
          <div className="actions">
            <button className="btn btn-accent" onClick={attempt} disabled={busy}>{busy ? 'Scoring…' : 'Score it'}</button>
          </div>
        </section>
      )}
    </div>
  );
}

/** Counts from 1 up to the rank, then shows the suffix. Small, and it makes the moment land. */
function CountUp({ to, suffix }: { to: number; suffix: string }) {
  const [n, setN] = useState(to === 1 ? 1 : 0);
  useEffect(() => {
    if (to <= 1) return;
    let frame = 0;
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / 600);
      setN(Math.max(1, Math.round(1 + (to - 1) * (1 - Math.pow(1 - t, 3)))));
      if (t < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [to]);
  return <>{n}{n === to ? suffix : ''}</>;
}

function ordinal(n: number) {
  const s = ['th', 'st', 'nd', 'rd'];
  const v = n % 100;
  return s[(v - 20) % 10] ?? s[v] ?? s[0];
}

function pct(v: number) {
  return Math.round(v * 100) + '%';
}
