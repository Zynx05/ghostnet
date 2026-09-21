'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';
import { api } from '../../lib/api';
import { useSession } from '../../lib/auth';
import type { Challenge, Thread } from '../../lib/types';
import { RequireRole } from '../../components/RequireRole';
import { Bubbles, Composer } from '../../components/Thread';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../../components/ui';

export default function InboxPage() {
  return <RequireRole role="candidate"><Inbox /></RequireRole>;
}

function Inbox() {
  const session = useSession();
  const [threads, setThreads] = useState<Thread[] | null>(null);
  const [openId, setOpenId] = useState<number | null>(null);
  const [challenge, setChallenge] = useState<Challenge | null>(null);
  const [search, setSearch] = useState('');
  const [flash, setFlash] = useState<FlashMessage>(null);

  async function load(keep?: number) {
    const rows = await api.inbox();
    setThreads(rows);
    setOpenId(keep ?? rows[0]?.challenge_id ?? null);
  }

  useEffect(() => {
    load().catch(e => { setFlash({ text: e.message, err: true }); setThreads([]); });
  }, []);

  // The right panel needs the challenge behind the conversation.
  useEffect(() => {
    if (openId === null) return;
    setChallenge(null);
    api.challenge(openId).then(setChallenge).catch(() => {});
  }, [openId]);

  const shown = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q || !threads) return threads ?? [];
    return threads.filter(t =>
      t.company.toLowerCase().includes(q) ||
      t.title.toLowerCase().includes(q) ||
      t.messages.some(m => m.body.toLowerCase().includes(q)),
    );
  }, [threads, search]);

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
    <div className="page page-wide">
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
          {/* Left: who has written to you. */}
          <aside className="thread-list">
            <div className="thread-list-head">
              <span>Inbox</span>
              <span className="thread-list-count">{threads.length}</span>
            </div>
            <div className="thread-search">
              <input
                className="field-input"
                value={search}
                placeholder="Search"
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <div className="thread-scroll">
              {shown.map(t => (
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
              {shown.length === 0 && <div className="thread-none">Nothing matches that.</div>}
            </div>
          </aside>

          {/* Middle: the conversation. */}
          <div className="thread-view">
            {open && (
              <>
                <header className="thread-head">
                  <div className="thread-avatar">{initials(open.company)}</div>
                  <div style={{ minWidth: 0 }}>
                    <div className="thread-head-who">{open.company}</div>
                    <div className="thread-head-sub">{open.title}</div>
                  </div>
                </header>
                <Bubbles thread={open} mine="ghost" />
                <Composer onSend={send} />
              </>
            )}
          </div>

          {/* Right: what the conversation is about. */}
          <aside className="thread-side">
            {open && (
              <>
                <div className="side-avatar">{initials(open.company)}</div>
                <div className="side-name">{open.company}</div>
                <div className="side-sub">is talking to {session?.name}</div>

                <div className="side-stats">
                  <div><strong>{open.count}</strong><span>messages</span></div>
                  <div><strong>{open.messages.filter(m => m.sender === 'ghost').length}</strong><span>from you</span></div>
                </div>

                <div className="side-block">
                  <span className="algo-tag">Challenge</span>
                  <Link href={`/challenge/${open.challenge_id}`} className="side-link">{open.title}</Link>
                </div>

                {challenge && (
                  <>
                    <div className="side-block">
                      <span className="algo-tag">Status</span>
                      <Badge tone={challenge.revealed ? 'good' : 'neutral'}>
                        {challenge.revealed ? 'Winner announced' : 'Open'}
                      </Badge>
                    </div>
                    {challenge.reward && (
                      <div className="side-block">
                        <span className="algo-tag">Reward</span>
                        <Badge tone="accent">{challenge.reward}</Badge>
                      </div>
                    )}
                    <div className="side-block">
                      <span className="algo-tag">Closes</span>
                      <div className="side-plain">day {challenge.end_day}</div>
                    </div>
                  </>
                )}

                <Link href={`/challenge/${open.challenge_id}`} className="btn btn-wide side-cta">
                  Open challenge
                </Link>
              </>
            )}
          </aside>
        </section>
      )}
    </div>
  );
}

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();
}
