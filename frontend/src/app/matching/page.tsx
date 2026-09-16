'use client';

import { useState } from 'react';
import { api } from '../../lib/api';
import type { MatchResponse } from '../../lib/types';
import { Flash, type FlashMessage } from '../../components/ui';

/**
 * Three companies hiring in the same week, three people who won challenges.
 * The lists are arranged so the clash is obvious: Northwind and Vega both want
 * their first pick from the same small group.
 */
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

  // Who did more than one company put first?
  const firstPicks = Object.entries(COMPANIES).map(([c, order]) => [c, order[0]] as const);
  const contested = firstPicks
    .map(([, pick]) => pick)
    .filter((pick, _, all) => all.filter(p => p === pick).length > 1);

  return (
    <div className="page">
      <section className="card">
        <h1 className="page-title">Offer round</h1>
        <div className="card-meta">
          When several challenges finish in the same week, the same strong people win
          more than one. Everybody cannot take every job, so this decides who goes
          where in one go.
        </div>
      </section>

      <Flash message={flash} />

      <section className="card">
        <div className="card-title">The problem</div>
        <div className="card-body">
          Two people are wanted first by two different companies. If each company
          just calls its favourite, one gets a yes and the other gets a no and has
          to start again, by which point the people they wanted next have gone.
        </div>
        <div className="cluster" style={{ marginTop: 12 }}>
          {firstPicks.map(([company, pick]) => (
            <div key={company} className={contested.includes(pick) ? 'pick pick-clash' : 'pick'}>
              <div className="algo-tag">{company} wants first</div>
              <div className="pick-name">{pick}</div>
            </div>
          ))}
        </div>
      </section>

      <div className="cluster" style={{ alignItems: 'stretch' }}>
        <section className="card" style={{ flex: 1, minWidth: 240 }}>
          <div className="card-title">Who each person wants</div>
          {Object.entries(CANDIDATES).map(([who, order]) => (
            <div key={who} className="pref">
              <span className="algo-tag">{who}</span>
              <div className="pref-order">{order.join(' › ')}</div>
            </div>
          ))}
        </section>
        <section className="card" style={{ flex: 1, minWidth: 240 }}>
          <div className="card-title">Who each company wants</div>
          {Object.entries(COMPANIES).map(([who, order]) => (
            <div key={who} className="pref">
              <span className="algo-tag">{who}</span>
              <div className="pref-order">{order.join(' › ')}</div>
            </div>
          ))}
        </section>
      </div>

      {!result ? (
        <section className="card">
          <div className="row-between">
            <div>
              <div className="card-title">Ready to decide</div>
              <div className="card-meta">Everyone gets one offer and no clashes are left.</div>
            </div>
            <button className="btn btn-accent" onClick={run}>Run the offer round</button>
          </div>
        </section>
      ) : (
        <>
          <section className="card">
            <div className="card-title">Everybody placed</div>
            <div className="card-meta">
              No company and person here would both rather have had each other, so
              nobody has a reason to back out.
            </div>
            <div className="table-wrap">
              <table className="data">
                <thead><tr><th>Company</th><th>Hires</th></tr></thead>
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
            <div className="card-title">How it was settled</div>
            <div className="card-meta">
              People ask their favourite company first. A company holds the best offer
              it has so far and lets the others go, and anyone let go asks the next
              company on their list.
            </div>
            <ol className="log-list">
              {result.log.map((line, i) => <li key={i}>{line}</li>)}
            </ol>
          </section>
        </>
      )}
    </div>
  );
}
