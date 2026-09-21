'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../lib/api';
import { useSession } from '../lib/auth';
import type { Challenge } from '../lib/types';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../components/ui';

export default function ChallengesPage() {
  const session = useSession();
  const [rows, setRows] = useState<Challenge[] | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);

  useEffect(() => {
    api.challenges()
      .then(setRows)
      .catch(e => { setFlash({ text: e.message, err: true }); setRows([]); });
  }, []);

  return (
    <div className="page">
      <section className="hero">
        <h1 className="display">
          Hiring based on<br />what you <mark>can do.</mark>
        </h1>
        <p className="lede">
          Companies post real problems. You answer as a ghost. The best work wins,
          and only then does anyone learn who you are.
        </p>
        {session?.role === 'candidate' && (
          <div className="hero-actions">
            <Link href="/practice" className="btn">Warm up first</Link>
            <span className="hero-you">You are <strong>{session.name}</strong></span>
          </div>
        )}
        {session?.role === 'company' && (
          <div className="hero-actions">
            <Link href="/post" className="btn btn-accent">Post a challenge</Link>
          </div>
        )}
      </section>

      <Flash message={flash} />

      {rows === null && <div className="card"><Skeleton rows={3} /></div>}

      {rows !== null && rows.length === 0 && (
        <div className="card">
          <EmptyState title="No challenges yet" description="Be the first company to post one." />
        </div>
      )}

      {(rows ?? []).map((c, i) => (
        <Link key={c.id} href={`/challenge/${c.id}`} className="card row-card">
          <div className="row-index">{String(i + 1).padStart(2, '0')}</div>
          <div className="row-main">
            <div className="row-between">
              <div>
                <div className="card-title">{c.title}</div>
                <div className="card-meta">
                  {c.company} · {c.entries ?? 0} {c.entries === 1 ? 'entry' : 'entries'}
                </div>
              </div>
              <Badge tone={c.revealed ? 'good' : 'neutral'}>
                {c.revealed ? 'Winner announced' : 'Open'}
              </Badge>
            </div>
            <p className="card-body">{c.statement}</p>
            {c.reward && <div style={{ marginTop: 10 }}><Badge tone="accent">{c.reward}</Badge></div>}
          </div>
          <div className="row-arrow" aria-hidden="true">→</div>
        </Link>
      ))}
    </div>
  );
}
