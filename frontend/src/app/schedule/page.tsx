'use client';

import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import type { ScheduleResponse, Window } from '../../lib/types';
import { EmptyState, Flash, type FlashMessage } from '../../components/ui';

const DAY_NAMES = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
const WEEKS = 4;
const DAYS = WEEKS * 7;

/** Day 0 of the schedule is today. Everything else counts forward from it. */
function dateFor(offset: number) {
  const d = new Date();
  d.setHours(0, 0, 0, 0);
  d.setDate(d.getDate() + offset);
  return d;
}

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

  // The calendar starts on the Monday of this week, so the columns line up with
  // real weekdays instead of starting wherever day 0 happens to fall.
  const today = dateFor(0);
  const weekdayOfToday = (today.getDay() + 6) % 7;
  const firstCell = -weekdayOfToday;

  const cells = Array.from({ length: DAYS }, (_, i) => firstCell + i);

  function windowsOn(day: number): Window[] {
    return data!.sorted_by_finish.filter(w => day >= w.start && day < w.end);
  }

  const monthLabel = dateFor(firstCell).toLocaleDateString(undefined, {
    month: 'long', year: 'numeric',
  });

  return (
    <div className="page">
      <section className="card">
        <h1 className="page-title">Challenge calendar</h1>
        <div className="card-meta">
          Two challenges running at once split the crowd, so fewer people enter each
          one. The calendar fits in as many as it can without any overlap.
        </div>
      </section>

      <Flash message={flash} />

      <section className="card">
        <div className="row-between">
          <div className="card-title">{monthLabel}</div>
          <div className="cluster">
            <span className="legend-dot legend-run" /> <span className="card-meta">Running</span>
            <span className="legend-dot legend-clash" /> <span className="card-meta">Cannot fit</span>
          </div>
        </div>

        <div className="cal">
          {DAY_NAMES.map(d => <div key={d} className="cal-head">{d}</div>)}

          {cells.map(day => {
            const date = dateFor(day);
            const running = windowsOn(day);
            const isToday = day === 0;
            const firstOfMonth = date.getDate() === 1;
            return (
              <div key={day} className={isToday ? 'cal-cell cal-today' : 'cal-cell'}>
                <div className="cal-date">
                  {firstOfMonth
                    ? date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
                    : date.getDate()}
                </div>
                {running.map(w => (
                  <div
                    key={w.title}
                    className={chosen.has(w.title) ? 'cal-chip cal-chip-run' : 'cal-chip cal-chip-clash'}
                    title={`${w.title} · day ${w.start} to ${w.end}`}
                  >
                    {w.title}
                  </div>
                ))}
              </div>
            );
          })}
        </div>
      </section>

      <section className="card">
        <div className="card-title">Running ({data.chosen.length})</div>
        {data.chosen.map(w => (
          <div key={w.title} className="row-between sched-row">
            <span>{w.title}</span>
            <span className="card-meta">
              {dateFor(w.start).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
              {' to '}
              {dateFor(w.end).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
            </span>
          </div>
        ))}
      </section>

      {data.dropped.length > 0 && (
        <section className="card">
          <div className="card-title">Could not fit ({data.dropped.length})</div>
          <div className="card-meta">
            These overlap something already running. Move them and they go straight in.
          </div>
          {data.dropped.map(w => (
            <div key={w.title} className="row-between sched-row">
              <span>{w.title}</span>
              <span className="card-meta">
                {dateFor(w.start).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                {' to '}
                {dateFor(w.end).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
              </span>
            </div>
          ))}
        </section>
      )}
    </div>
  );
}
