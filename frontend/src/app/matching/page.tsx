'use client';

import { useState } from 'react';
import { api } from '../../lib/api';
import type { MatchResponse } from '../../lib/types';
import { EmptyState, Flash, type FlashMessage } from '../../components/ui';

const CANDIDATES: Record<string, string[]> = {
  ghost_001: ['Northwind', 'Vega', 'Meridian'],
  ghost_002: ['Northwind', 'Meridian', 'Vega'],
  ghost_003: ['Vega', 'Northwind', 'Meridian'],
};

const COMPANIES: Record<string, string[]> = {
  Northwind: ['ghost_002', 'ghost_001', 'ghost_003'],
  Vega: ['ghost_001', 'ghost_003', 'ghost_002'],
  Meridian: ['ghost_003', 'ghost_002', 'ghost_001'],
};

export default function MatchingPage() {
  const [result, setResult] = useState<MatchResponse | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);

  async function run() {
    try {
      setResult(await api.match(CANDIDATES, COMPANIES));
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
    }
  }

  return (
    <div className="page">
      <section className="card">
        <div className="row-between">
          <div>
            <h1 className="page-title">Matches</h1>
            <div className="card-meta">
              Winners rank the companies. Companies rank the winners. Everyone gets a
              match nobody would trade away.
            </div>
          </div>
          <button className="btn btn-accent" onClick={run}>Find matches</button>
        </div>
      </section>

      <Flash message={flash} />

      <div className="cluster" style={{ alignItems: 'stretch' }}>
        <section className="card" style={{ flex: 1, minWidth: 240 }}>
          <div className="card-title">Candidates want</div>
          {Object.entries(CANDIDATES).map(([who, order]) => (
            <div key={who} className="pref">
              <span className="algo-tag">{who}</span>
              <div className="pref-order">{order.join(' › ')}</div>
            </div>
          ))}
        </section>
        <section className="card" style={{ flex: 1, minWidth: 240 }}>
          <div className="card-title">Companies want</div>
          {Object.entries(COMPANIES).map(([who, order]) => (
            <div key={who} className="pref">
              <span className="algo-tag">{who}</span>
              <div className="pref-order">{order.join(' › ')}</div>
            </div>
          ))}
        </section>
      </div>

      {!result ? (
        <div className="card"><EmptyState title="No matches yet" description="Press Find matches." /></div>
      ) : (
        <>
          <section className="card">
            <div className="card-title">Matches</div>
            <div className="table-wrap">
              <table className="data">
                <thead><tr><th>Company</th><th>Candidate</th></tr></thead>
                <tbody>
                  {result.pairs.map(p => (
                    <tr key={p.company}>
                      <td>{p.company}</td>
                      <td style={{ fontFamily: 'var(--mono)', fontSize: 12 }}>{p.candidate}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <section className="card">
            <div className="card-title">How it was decided</div>
            <ol className="log-list">
              {result.log.map((line, i) => <li key={i}>{line}</li>)}
            </ol>
          </section>
        </>
      )}
    </div>
  );
}
