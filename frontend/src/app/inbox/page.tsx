'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../../lib/api';
import { ensureGhost } from '../../lib/ghost';
import type { Message } from '../../lib/types';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../../components/ui';

const LABEL: Record<Message['kind'], { text: string; tone: 'accent' | 'neutral' | 'good' }> = {
  tap: { text: 'Wants to talk', tone: 'accent' },
  whisper: { text: 'Feedback', tone: 'neutral' },
  answer: { text: 'Answered', tone: 'good' },
};

export default function InboxPage() {
  const [rows, setRows] = useState<Message[] | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);

  useEffect(() => {
    ensureGhost()
      .then(() => api.inbox())
      .then(setRows)
      .catch(e => { setFlash({ text: e.message, err: true }); setRows([]); });
  }, []);

  return (
    <div className="page">
      <section className="card hero">
        <h1 className="page-title">Inbox</h1>
        <div className="card-meta">
          Everything comes to you in writing. Nobody can call you. A tap means a
          company wants to talk, and you decide whether to answer.
        </div>
      </section>

      <Flash message={flash} />
      {rows === null && <div className="card"><Skeleton rows={3} /></div>}

      {rows !== null && rows.length === 0 && (
        <div className="card">
          <EmptyState title="Nothing yet" description="Enter a challenge. Taps and feedback land here." />
        </div>
      )}

      {(rows ?? []).map(m => (
        <section key={m.id} className="card">
          <div className="row-between">
            <div className="card-meta">
              <Link href={`/challenge/${m.challenge_id}`} className="link">{m.title}</Link> · {m.company}
            </div>
            <Badge tone={LABEL[m.kind].tone}>{LABEL[m.kind].text}</Badge>
          </div>
          <p className="card-body" style={{ whiteSpace: 'pre-wrap' }}>{m.body}</p>
        </section>
      ))}
    </div>
  );
}
