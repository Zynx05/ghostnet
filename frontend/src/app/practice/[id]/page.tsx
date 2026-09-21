'use client';

import { useEffect, useState, use } from 'react';
import Link from 'next/link';
import { api } from '../../../lib/api';
import { ensureGhost } from '../../../lib/ghost';
import type { Challenge, PracticeResult } from '../../../lib/types';
import { Badge, EmptyState, Flash, type FlashMessage } from '../../../components/ui';

export default function PracticeAttemptPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const challengeId = Number(id);

  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [content, setContent] = useState('');
  const [result, setResult] = useState<PracticeResult | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.challenge(challengeId).then(setChallenge).catch(e => setFlash({ text: e.message, err: true }));
  }, [challengeId]);

  async function attempt() {
    if (!content.trim()) {
      setFlash({ text: 'Write something first.', err: true });
      return;
    }
    setBusy(true);
    try {
      await ensureGhost();
      setResult(await api.practice(challengeId, content));
      setFlash(null);
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    } finally {
      setBusy(false);
    }
  }

  if (!challenge) {
    return <div className="page"><Flash message={flash} /><div className="card"><EmptyState title="Loading" /></div></div>;
  }

  const ordinal = (n: number) => n + (['th', 'st', 'nd', 'rd'][(n % 100 > 10 && n % 100 < 14) ? 0 : Math.min(n % 10, 4) % 4] ?? 'th');

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
          <div className="result-rank">{ordinal(result.would_rank)} <span>of {result.out_of}</span></div>
          <div className="result-scores">
            <div><span className="algo-tag">Relevance</span>{pct(result.scores.relevance)}</div>
            <div><span className="algo-tag">Quality</span>{pct(result.scores.quality)}</div>
            <div><span className="algo-tag">Structure</span>{pct(result.scores.structure)}</div>
            <div><span className="algo-tag">Score</span>{result.scores.final_score.toFixed(2)}</div>
          </div>
          <div className="actions">
            <button className="btn btn-ghost" onClick={() => setResult(null)}>Try again</button>
            {!challenge.practice && (
              <Link href={`/challenge/${challenge.id}`} className="btn">See the real results</Link>
            )}
          </div>
        </section>
      ) : (
        <section className="card">
          <div className="card-title">Your attempt</div>
          <div className="field">
            <textarea className="field-textarea" rows={9} value={content}
              placeholder="Paste your code or your answer"
              onChange={e => setContent(e.target.value)} />
          </div>
          <div className="actions">
            <button className="btn btn-accent" onClick={attempt} disabled={busy}>
              {busy ? 'Scoring…' : 'Score it'}
            </button>
          </div>
        </section>
      )}
    </div>
  );
}

function pct(v: number) {
  return Math.round(v * 100) + '%';
}
