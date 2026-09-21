'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../../lib/api';
import type { MyPage } from '../../lib/types';
import { RequireRole } from '../../components/RequireRole';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../../components/ui';

export default function MePage() {
  return <RequireRole role="candidate"><Me /></RequireRole>;
}

function Me() {
  const [me, setMe] = useState<MyPage | null>(null);
  const [name, setName] = useState('');
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
      setFlash({ text: name.trim() ? 'Saved. A company only sees this if they pay to unmask you.' : 'Cleared. You stay masked even if you win.' });
      load();
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  if (!me) return <div className="page"><Flash message={flash} /><div className="card"><Skeleton rows={4} /></div></div>;

  const wins = me.proofs.length;

  return (
    <div className="page">
      <section className="credential">
        <div className="credential-head">
          <div>
            <span className="algo-tag">Your ghost</span>
            <div className="credential-id">{me.ghost.name}</div>
          </div>
          <div className="credential-count">
            <div className="credential-count-n">{wins}</div>
            <div className="algo-tag">verified {wins === 1 ? 'win' : 'wins'}</div>
          </div>
        </div>
        {me.check_code && (
          <div className="credential-foot">
            <span className="algo-tag">Check code · give this to an employer</span>
            <div className="hash">{me.check_code}</div>
          </div>
        )}
      </section>

      <Flash message={flash} />

      <section className="card">
        <div className="card-title">Your real name</div>
        <div className="card-meta">Optional. A company pays Rs 1,500 to see it, and only after you have entered and they have closed the challenge. Leave it blank to stay masked no matter what.</div>
        <div className="qa-ask" style={{ marginTop: 10 }}>
          <input className="field-input" value={name} placeholder="Leave blank to stay masked" onChange={e => setName(e.target.value)} />
          <button className="btn btn-sm btn-accent" onClick={saveName}>Save</button>
        </div>
      </section>

      {me.proofs.length > 0 && (
        <section className="card">
          <div className="card-title">Skill Proof</div>
          <div className="card-meta">Each win is sealed to the one before it. <Link href="/chain" className="link">See the whole chain</Link>.</div>
          <div className="chain">
            {me.proofs.map((p, i) => (
              <div key={p.challenge_id} className="chain-item">
                <div className="chain-rail"><div className="chain-dot">✓</div>{i < me.proofs.length - 1 && <div className="chain-line" />}</div>
                <div className="chain-body">
                  <div className="chain-title">{p.title}</div>
                  <div className="card-meta">{p.company}</div>
                  <div className="hash" style={{ marginTop: 4 }}>{p.seal.slice(0, 32)}…</div>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="card">
        <div className="card-title">Your entries ({me.entries.length})</div>
        {me.entries.length === 0 ? (
          <EmptyState title="No entries yet" description="Open a challenge and enter it. Or warm up under Practice first." />
        ) : (
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th>Challenge</th><th>Company</th><th className="num">Rank</th><th></th></tr></thead>
              <tbody>
                {me.entries.map(e => (
                  <tr key={e.challenge_id}>
                    <td><Link href={`/challenge/${e.challenge_id}`} className="link">{e.title}</Link></td>
                    <td>{e.company}</td>
                    <td className="num">{e.rank ? `#${e.rank}` : '—'}</td>
                    <td>{e.rank === 1 && e.revealed ? <Badge tone="good">Won</Badge> : e.revealed ? <Badge>Closed</Badge> : e.rank ? <Badge tone="accent">Ranked</Badge> : <Badge>Waiting</Badge>}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {me.practice.length > 0 && (
        <section className="card">
          <div className="card-title">Practice ({me.practice.length})</div>
          <div className="table-wrap">
            <table className="data">
              <thead><tr><th>Challenge</th><th className="num">Would have ranked</th><th className="num">Score</th></tr></thead>
              <tbody>
                {me.practice.map((p, i) => (
                  <tr key={i}>
                    <td><Link href={`/practice/${p.challenge_id}`} className="link">{p.title.replace(/^Warm up: /, '')}</Link></td>
                    <td className="num">#{p.would_rank} of {p.out_of}</td>
                    <td className="num">{p.final_score.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </div>
  );
}
