'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../../lib/api';
import type { MyPage } from '../../lib/types';
import { RequireRole } from '../../components/RequireRole';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../../components/ui';

export default function MePage() {
  return <RequireRole role="candidate"><Profile /></RequireRole>;
}

function Profile() {
  const [me, setMe] = useState<MyPage | null>(null);
  const [name, setName] = useState('');
  const [editing, setEditing] = useState(false);
  const [flash, setFlash] = useState<FlashMessage>(null);

  async function load() {
    const data = await api.me();
    setMe(data);
    setName(data.ghost.real_name);
  }

  useEffect(() => { load().catch(e => setFlash({ text: e.message, err: true })); }, []);

  async function saveName() {
    try {
      await api.setName(name);
      setEditing(false);
      setFlash({
        text: name.trim()
          ? 'Saved. A company only sees this if they pay to unmask you.'
          : 'Cleared. You stay masked even if you win.',
      });
      load();
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  if (!me) return <div className="page"><Flash message={flash} /><div className="card"><Skeleton rows={5} /></div></div>;

  const wins = me.proofs.length;
  const ranked = me.entries.filter(e => e.rank).length;
  const initials = me.ghost.name.split(/\s+/).slice(0, 2).map(w => w[0]).join('');

  return (
    <div className="page">
      <section className="profile">
        <div className="profile-banner" aria-hidden="true" />
        <div className="profile-head">
          <div className="profile-avatar">{initials}</div>
          <div className="profile-id">
            <h1 className="profile-name">{me.ghost.name}</h1>
            <div className="profile-sub">
              {me.ghost.real_name
                ? <>Real name on file · shown only if a company pays</>
                : <>No real name · you stay masked even if you win</>}
            </div>
          </div>
          <div className="profile-stats">
            <div><strong>{wins}</strong><span>wins</span></div>
            <div><strong>{me.entries.length}</strong><span>entries</span></div>
            <div><strong>{ranked}</strong><span>ranked</span></div>
          </div>
        </div>
        <div className="profile-actions">
          <button className="btn btn-accent" onClick={() => setEditing(!editing)}>
            {editing ? 'Cancel' : me.ghost.real_name ? 'Edit real name' : 'Add real name'}
          </button>
          <Link href="/practice" className="btn">Practice</Link>
          <Link href="/chain" className="btn btn-ghost">Proof chain</Link>
        </div>
        {editing && (
          <div className="profile-edit">
            <input
              className="field-input"
              value={name}
              placeholder="Leave blank to stay masked"
              onChange={e => setName(e.target.value)}
              autoFocus
            />
            <button className="btn btn-accent" onClick={saveName}>Save</button>
          </div>
        )}
      </section>

      <Flash message={flash} />

      <div className="profile-grid">
        <aside className="profile-col">
          <section className="card panel">
            <div className="panel-title">About</div>
            <p className="panel-text">
              You are <strong>{me.ghost.name}</strong>. That name is the only thing a
              company sees while it is judging your work. Your real name sits behind
              it and costs Rs 1,500 to reveal, after a challenge closes.
            </p>
          </section>

          {me.check_code && (
            <section className="card panel">
              <div className="panel-title">Check code</div>
              <p className="panel-text">Give this to an employer and they can verify any win.</p>
              <div className="hash" style={{ marginTop: 8 }}>{me.check_code}</div>
            </section>
          )}

          <section className="card panel">
            <div className="panel-title">Practice ({me.practice.length})</div>
            {me.practice.length === 0 ? (
              <p className="panel-text">Nothing yet. <Link href="/practice" className="link">Warm up</Link>.</p>
            ) : (
              me.practice.slice(0, 5).map((p, i) => (
                <div key={i} className="mini-row">
                  <Link href={`/practice/${p.challenge_id}`} className="mini-title">
                    {p.title.replace(/^Warm up: /, '')}
                  </Link>
                  <span className="mini-rank">#{p.would_rank}/{p.out_of}</span>
                </div>
              ))
            )}
          </section>
        </aside>

        <div className="profile-col">
          <section className="card panel">
            <div className="panel-title">Skill Proof</div>
            {me.proofs.length === 0 ? (
              <p className="panel-text">
                No verified wins yet. Win a challenge and it gets sealed here, linked
                to the one before it.
              </p>
            ) : (
              <div className="chain">
                {me.proofs.map((p, i) => (
                  <div key={p.challenge_id} className="chain-item">
                    <div className="chain-rail">
                      <div className="chain-dot">✓</div>
                      {i < me.proofs.length - 1 && <div className="chain-line" />}
                    </div>
                    <div className="chain-body">
                      <div className="chain-title">{p.title}</div>
                      <div className="card-meta">{p.company}</div>
                      <div className="hash" style={{ marginTop: 4 }}>{p.seal.slice(0, 32)}…</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="card panel">
            <div className="panel-title">Entries ({me.entries.length})</div>
            {me.entries.length === 0 ? (
              <EmptyState title="No entries yet" description="Open a challenge and enter it." />
            ) : (
              me.entries.map(e => (
                <div key={e.challenge_id} className="entry-row">
                  <div className="entry-rank">{e.rank ? `#${e.rank}` : '—'}</div>
                  <div className="entry-main">
                    <Link href={`/challenge/${e.challenge_id}`} className="entry-title">{e.title}</Link>
                    <div className="card-meta">{e.company}</div>
                  </div>
                  {e.rank === 1 && e.revealed ? <Badge tone="good">Won</Badge>
                    : e.revealed ? <Badge>Closed</Badge>
                    : e.rank ? <Badge tone="accent">Ranked</Badge>
                    : <Badge>Waiting</Badge>}
                </div>
              ))
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
