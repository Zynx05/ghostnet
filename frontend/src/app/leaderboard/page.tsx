'use client';

import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import { readGhost } from '../../lib/ghost';
import type { LeaderRow } from '../../lib/types';
import { EmptyState, Flash, Skeleton, type FlashMessage } from '../../components/ui';

export default function LeaderboardPage() {
  const [rows, setRows] = useState<LeaderRow[] | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);
  const myId = readGhost()?.ghost_id;

  useEffect(() => {
    api.leaderboard()
      .then(setRows)
      .catch(e => { setFlash({ text: e.message, err: true }); setRows([]); });
  }, []);

  return (
    <div className="page">
      <section className="card hero">
        <h1 className="page-title">Leaderboard</h1>
        <div className="card-meta">Ghosts, by verified wins. Names only, never people.</div>
      </section>

      <Flash message={flash} />
      {rows === null && <div className="card"><Skeleton rows={5} /></div>}

      {rows !== null && rows.length === 0 && (
        <div className="card"><EmptyState title="Nobody has entered anything yet" /></div>
      )}

      {rows !== null && rows.length > 0 && (
        <section className="card">
          <div className="table-wrap" style={{ marginTop: 0 }}>
            <table className="data">
              <thead><tr><th className="num">#</th><th>Ghost</th><th className="num">Wins</th><th className="num">Entries</th></tr></thead>
              <tbody>
                {rows.map((r, i) => (
                  <tr key={r.ghost_id} className={r.ghost_id === myId ? 'row-me' : undefined}>
                    <td className="num">{i + 1}</td>
                    <td>{r.name}{r.ghost_id === myId && <span className="you"> you</span>}</td>
                    <td className="num"><strong>{r.wins}</strong></td>
                    <td className="num">{r.entries}</td>
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
