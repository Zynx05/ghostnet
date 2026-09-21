'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../../lib/api';
import type { Challenge } from '../../lib/types';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../../components/ui';

export default function PracticePage() {
  const [rows, setRows] = useState<Challenge[] | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);

  useEffect(() => {
    api.practiceList()
      .then(setRows)
      .catch(e => { setFlash({ text: e.message, err: true }); setRows([]); });
  }, []);

  const warmups = (rows ?? []).filter(c => c.practice);
  const closed = (rows ?? []).filter(c => !c.practice);

  return (
    <div className="page">
      <section className="card hero">
        <h1 className="page-title">Practice</h1>
        <div className="card-meta">
          Nothing here counts. You get scored, you see where you would have ranked,
          and nobody else ever sees it. Try things.
        </div>
      </section>

      <Flash message={flash} />
      {rows === null && <div className="card"><Skeleton rows={3} /></div>}

      {warmups.length > 0 && (
        <>
          <div className="section-label">Warm ups</div>
          {warmups.map(c => (
            <Link key={c.id} href={`/practice/${c.id}`} className="card">
              <div className="row-between">
                <div className="card-title">{c.title.replace(/^Warm up: /, '')}</div>
                <Badge>Warm up</Badge>
              </div>
              <p className="card-body">{c.statement}</p>
            </Link>
          ))}
        </>
      )}

      {closed.length > 0 && (
        <>
          <div className="section-label">Real challenges, now closed</div>
          {closed.map(c => (
            <Link key={c.id} href={`/practice/${c.id}`} className="card">
              <div className="row-between">
                <div>
                  <div className="card-title">{c.title}</div>
                  <div className="card-meta">{c.company} · {c.entries} real entries to rank against</div>
                </div>
                <Badge tone="good">Closed</Badge>
              </div>
              <p className="card-body">{c.statement}</p>
            </Link>
          ))}
        </>
      )}

      {rows !== null && rows.length === 0 && (
        <div className="card"><EmptyState title="Nothing to practice on yet" /></div>
      )}
    </div>
  );
}
