'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '../../lib/api';
import { saveSession, useSession } from '../../lib/auth';
import type { Challenge } from '../../lib/types';
import { RequireRole } from '../../components/RequireRole';
import { Badge, EmptyState, Flash, Skeleton, type FlashMessage } from '../../components/ui';

export default function CompanyPage() {
  return <RequireRole role="company"><Dashboard /></RequireRole>;
}

function Dashboard() {
  const session = useSession();
  const [rows, setRows] = useState<Challenge[] | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.companyChallenges().then(setRows).catch(e => { setFlash({ text: e.message, err: true }); setRows([]); });
  }, []);

  async function topup() {
    setBusy(true);
    try {
      saveSession(await api.topup());
      setFlash({ text: 'Rs 10,000 added. Demo money, no card was charged.' });
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <section className="balance">
        <div>
          <span className="algo-tag">Balance</span>
          <div className="balance-amount">Rs {(session?.balance_pkr ?? 0).toLocaleString()}</div>
          <div className="balance-note">Rs 1,500 to unmask one candidate. Ranking and closing are free.</div>
        </div>
        <div className="balance-actions">
          <button className="btn btn-light" onClick={topup} disabled={busy}>
            {busy ? 'Adding…' : 'Add Rs 10,000'}
          </button>
          <span className="balance-hint">Demo. A real launch puts JazzCash here.</span>
        </div>
      </section>

      <Flash message={flash} />

      <div className="row-between">
        <div className="section-label">Your challenges</div>
        <Link href="/post" className="btn btn-sm btn-accent">Post a challenge</Link>
      </div>

      {rows === null && <div className="card"><Skeleton rows={3} /></div>}
      {rows !== null && rows.length === 0 && (
        <div className="card">
          <EmptyState title="You have not posted anything yet" description="Post a real problem and let people answer it without names." />
        </div>
      )}
      {(rows ?? []).map(c => (
        <Link key={c.id} href={`/challenge/${c.id}`} className="card">
          <div className="row-between">
            <div>
              <div className="card-title">{c.title}</div>
              <div className="card-meta">{c.entries ?? 0} {c.entries === 1 ? 'entry' : 'entries'} · closes day {c.end_day}</div>
            </div>
            <Badge tone={c.revealed ? 'good' : c.entries ? 'accent' : 'neutral'}>
              {c.revealed ? 'Closed' : c.entries ? 'Ready to rank' : 'Waiting for entries'}
            </Badge>
          </div>
        </Link>
      ))}
    </div>
  );
}
