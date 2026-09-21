'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../../lib/api';
import type { Thread } from '../../lib/types';
import { RequireRole } from '../../components/RequireRole';
import { Bubbles, Composer } from '../../components/Thread';
import { EmptyState, Flash, Skeleton, type FlashMessage } from '../../components/ui';

export default function InboxPage() {
  return <RequireRole role="candidate"><Inbox /></RequireRole>;
}

function Inbox() {
  const [threads, setThreads] = useState<Thread[] | null>(null);
  const [openId, setOpenId] = useState<number | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);

  async function load(keep?: number) {
    const rows = await api.inbox();
    setThreads(rows);
    setOpenId(keep ?? rows[0]?.challenge_id ?? null);
  }

  useEffect(() => {
    load().catch(e => { setFlash({ text: e.message, err: true }); setThreads([]); });
  }, []);

  const open = threads?.find(t => t.challenge_id === openId) ?? null;

  async function send(text: string) {
    if (!open) return;
    try {
      await api.reply(open.challenge_id, text);
      await load(open.challenge_id);
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  if (threads === null) {
    return <div className="page"><div className="card"><Skeleton rows={4} /></div></div>;
  }

  return (
    <div className="page">
      <div className="row-between">
        <h1 className="page-title">Messages</h1>
        <span className="card-meta">Text only. Nobody can call you.</span>
      </div>

      <Flash message={flash} />

      {threads.length === 0 ? (
        <div className="card">
          <EmptyState
            title="No messages yet"
            description="Enter a challenge. When a company taps you or leaves feedback, it lands here."
          />
        </div>
      ) : (
        <section className="messenger">
          <aside className="thread-list">
            <div className="thread-list-head">Inbox</div>
            {threads.map(t => (
              <button
                key={t.challenge_id}
                className={t.challenge_id === openId ? 'thread-item on' : 'thread-item'}
                onClick={() => setOpenId(t.challenge_id)}
              >
                <div className="thread-avatar">{initials(t.company)}</div>
                <div className="thread-item-main">
                  <div className="thread-item-top">
                    <span className="thread-who">{t.company}</span>
                    <span className="thread-count">{t.count}</span>
                  </div>
                  <div className="thread-snippet">
                    {t.last_sender === 'ghost' && <span className="thread-you">You: </span>}
                    {t.last_body}
                  </div>
                </div>
              </button>
            ))}
          </aside>

          <div className="thread-view">
            {open && (
              <>
                <header className="thread-head">
                  <div>
                    <div className="thread-head-who">{open.company}</div>
                    <Link href={`/challenge/${open.challenge_id}`} className="thread-head-sub">
                      {open.title} →
                    </Link>
                  </div>
                  <div className="thread-avatar thread-avatar-lg">{initials(open.company)}</div>
                </header>
                <Bubbles thread={open} mine="ghost" />
                <Composer onSend={send} />
              </>
            )}
          </div>
        </section>
      )}
    </div>
  );
}

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();
}
