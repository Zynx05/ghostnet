'use client';

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
        <div className="card"><EmptyState title="Loading" /></div>
      </div>
    );
  }

  const chosen = new Set(data.chosen.map(w => w.title));
  const span = Math.max(1, ...data.sorted_by_finish.map(w => w.end));

  function bar(w: Window) {
    const left = (w.start / span) * 100;
    const width = Math.max(8, ((w.end - w.start) / span) * 100);
    const picked = chosen.has(w.title);
    return (
      <div key={w.title} style={{ marginTop: 12 }}>
        <div className="row-between">
          <span style={{ fontSize: 13 }}>{w.title}</span>
          <span className="card-meta">day {w.start} to {w.end} · {picked ? 'scheduled' : 'clashes'}</span>
        </div>
        <div className="timeline-bar">
          <div
            className={picked ? 'timeline-span timeline-span-chosen' : 'timeline-span timeline-span-dropped'}
            style={{ left: `${left}%`, width: `${width}%` }}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <section className="card">
        <h1 className="page-title">Calendar</h1>
        <div className="card-meta">
          Two challenges at once split the audience, so the calendar fits in as many as it can
          without overlap.
        </div>
      </section>

      <Flash message={flash} />

      <div className="tile-grid">
        <StatTile label="Proposed" value={data.sorted_by_finish.length} />
        <StatTile label="Scheduled" value={data.chosen.length} />
        <StatTile label="Clashing" value={data.dropped.length} tone={data.dropped.length ? 'attn' : undefined} />
      </div>

      <section className="card">
        <div className="card-title">Timeline</div>
        {data.sorted_by_finish.map(bar)}
      </section>
    </div>
  );
}
