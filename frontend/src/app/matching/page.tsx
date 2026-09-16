'use client';

/**
 * Member 8  Product Manager.
 * Gale Shapley on a table small enough to trace on the whiteboard.
 * The proposal log is shown on purpose, because the log is the explanation.
 */

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
      <div className="row-between">
        <div>
          <h1 className="page-title">Matching</h1>
          <p className="page-subtitle">
            Winners and companies both have preferences. Gale Shapley pairs them so
            that no candidate and company would rather have each other.
          </p>
        </div>
        <button className="btn btn-accent" onClick={run}>Run matching</button>
      </div>

      <Flash message={flash} />

      <div className="cluster" style={{ alignItems: 'flex-start' }}>
        <section className="card" style={{ flex: 1, minWidth: 260 }}>
          <div className="card-title">Candidate preferences</div>
          {Object.entries(CANDIDATES).map(([who, order]) => (
            <div key={who} style={{ marginTop: '0.5rem' }}>
              <span className="algo-tag">{who}</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                {order.join(' then ')}
              </div>
            </div>
          ))}
        </section>

        <section className="card" style={{ flex: 1, minWidth: 260 }}>
          <div className="card-title">Company preferences</div>
          {Object.entries(COMPANIES).map(([who, order]) => (
            <div key={who} style={{ marginTop: '0.5rem' }}>
              <span className="algo-tag">{who}</span>
              <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                {order.join(' then ')}
              </div>
            </div>
          ))}
        </section>
      </div>

      {!result && (
        <EmptyState
          title="Not run yet"
          description="Press Run matching to see the proposals and the final pairing."
        />
      )}

      {result && (
        <>
          <section className="card">
            <div className="row-between">
              <div className="card-title">Stable pairing</div>
              <span className="owner">gale shapley  O(n squared)</span>
            </div>
            <div className="table-wrap" style={{ marginTop: '0.75rem' }}>
              <table className="data">
                <thead>
                  <tr><th>Company</th><th>Candidate</th></tr>
                </thead>
                <tbody>
                  {result.pairs.map(p => (
                    <tr key={p.company}>
                      <td>{p.company}</td>
                      <td style={{ fontFamily: 'var(--font-mono)' }}>{p.candidate}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="card">
            <div className="card-title">What happened, proposal by proposal</div>
            <ol className="log-list">
              {result.log.map((line, i) => <li key={i}>{line}</li>)}
            </ol>
          </section>
        </>
      )}
    </div>
  );
}
