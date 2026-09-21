'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../lib/api';
import type { Challenge } from '../lib/types';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../components/ui';

export default function ChallengesPage() {
  const [rows, setRows] = useState<Challenge[] | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);

  useEffect(() => {
    api.challenges()
      .then(setRows)
      .catch(e => { setFlash({ text: e.message, err: true }); setRows([]); });
  }, []);

  return (
    <div className="page">
      <section className="card hero">
        <h1 className="page-title">Hiring based on what you can do</h1>
        <div className="card-meta">
          Companies post real problems. You answer under a ghost name. The best work
          wins, and only then does anyone learn who you are.
        </div>
      </section>

      <Flash message={flash} />

      {rows === null && <div className="card"><Skeleton rows={3} /></div>}

      {rows !== null && rows.length === 0 && (
        <div className="card">
          <EmptyState title="No challenges yet" description="Be the first company to post one." />
        </div>
      )}

      {(rows ?? []).map(c => (
        <Link key={c.id} href={`/challenge/${c.id}`} className="card">
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
          {c.reward && (
            <div style={{ marginTop: 10 }}><Badge tone="accent">{c.reward}</Badge></div>
          )}
        </Link>
      ))}
    </div>
  );
}
