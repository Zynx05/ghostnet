/**
 * Small shared pieces. Each one is a thin wrapper over a class in ghostnet.css.
 */

import type { ReactNode } from 'react';

export type BadgeTone = 'neutral' | 'good' | 'bad' | 'accent';

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: BadgeTone }) {
  const cls = tone === 'neutral' ? 'badge' : `badge badge-${tone}`;
  return <span className={cls}>{children}</span>;
}

export function StatTile({
  label, value, note, tone,
}: {
  label: string;
  value: ReactNode;
  note?: string;
  tone?: 'attn';
}) {
  return (
    <div className={tone === 'attn' ? 'tile tile-attn' : 'tile'}>
      <div className="tile-label">{label}</div>
      <div className="tile-value">{value}</div>
      {note && <div className="tile-note">{note}</div>}
    </div>
  );
}

export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="empty">
      <div className="empty-title">{title}</div>
      {description && <div className="empty-desc">{description}</div>}
    </div>
  );
}

export type FlashMessage = { text: string; err?: boolean } | null;

export function Flash({ message }: { message: FlashMessage }) {
  if (!message) return null;
  return <div className={message.err ? 'flash flash-err' : 'flash'}>{message.text}</div>;
}

export function Skeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div aria-busy="true">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="skeleton" style={{ width: `${100 - i * 15}%` }} />
      ))}
    </div>
  );
}
