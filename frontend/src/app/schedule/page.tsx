'use client';

/**
 * Member 9  UI and UX Designer.
 * Greedy interval scheduling, drawn on a timeline so the greedy choice is
 * something the examiner can see rather than something we claim.
 */

import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import type { ScheduleResponse, Window } from '../../lib/types';
import { EmptyState, Flash, StatTile, type FlashMessage } from '../../components/ui';

export default function SchedulePage() {
  const [data, setData] = useState<ScheduleResponse | null>(null);
  const [flash, setFlash] = useState<FlashMessage>(null);

  useEffect(() => {
    api.schedule().then(setData).catch(e => setFlash({ text: e.message, err: true }));
  }, []);

  if (!data) {
    return (
      <div className="page">
        <Flash message={flash} />
        <EmptyState title="Loading" description="The backend must be running on port 8000." />
      </div>
    );
  }

  const chosen = new Set(data.chosen.map(w => w.title));
  const span = Math.max(1, ...data.sorted_by_finish.map(w => w.end));

  function bar(w: Window) {
    const left = (w.start / span) * 100;
    const width = Math.max(6, ((w.end - w.start) / span) * 100);
    const picked = chosen.has(w.title);
    return (
      <div key={w.title} style={{ marginBottom: '0.75rem' }}>
        <span className="algo-tag">
          {w.title}  day {w.start} to {w.end}  {picked ? 'kept' : 'dropped'}
        </span>
        <div className="timeline-bar">
          <div
            className={picked ? 'timeline-span timeline-span-chosen' : 'timeline-span timeline-span-dropped'}
            style={{ left: `${left}%`, width: `${width}%` }}
          >
            {w.title}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1 className="page-title">Challenge windows</h1>
      <p className="page-subtitle">
        Two challenges cannot run at once without splitting the audience, so the
        calendar takes the window that finishes earliest and repeats.
      </p>

      <Flash message={flash} />

      <div className="tile-grid">
        <StatTile label="Windows offered" value={data.sorted_by_finish.length} />
        <StatTile label="Windows kept" value={data.chosen.length} note="greedy choice" />
        <StatTile
          label="Windows dropped"
          value={data.dropped.length}
          tone={data.dropped.length ? 'attn' : undefined}
          note="they overlap something already kept"
        />
      </div>

      <section className="card">
        <div className="row-between">
          <div>
            <div className="card-title">Sorted by finishing time</div>
            <div className="card-meta">
              The sort is the whole cost of this algorithm, which is why it is O(n log n).
            </div>
          </div>
          <span className="owner">greedy intervals</span>
        </div>
        <div style={{ marginTop: '1rem' }}>
          {data.sorted_by_finish.map(bar)}
        </div>
      </section>
    </div>
  );
}
