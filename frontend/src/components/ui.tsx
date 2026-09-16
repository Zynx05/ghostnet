/**
 * apps/web/src/components/ui.tsx
 * Shared pieces. Thin wrappers over the classes in components.css so the markup
 * stays inspectable and the CSS stays the source of truth.
 */
import type { ReactNode } from 'react';
import type { LucideIcon } from 'lucide-react';

/* ── Badge ───────────────────────────────────────────────────────────── */

export type BadgeTone = 'neutral' | 'good' | 'bad' | 'accent';

export function Badge({ children, tone = 'neutral' }: { children: ReactNode; tone?: BadgeTone }) {
  // Brutalist badges carry tone in the border and text, never a fill — a solid
  // fill would compete with the inverted "active" treatment used for state.
  const style =
    tone === 'good' ? { color: 'var(--good)', borderColor: 'var(--good)' }
      : tone === 'bad' ? { color: 'var(--bad)', borderColor: 'var(--bad)' }
        : tone === 'accent' ? { background: 'var(--text)', color: 'var(--bg)' }
          : undefined;
  return <span className="badge" style={style}>{children}</span>;
}

/**
 * Verification state as a badge. Only `verified` is eligible for activation, so
 * it is the only good state; `stale_disputed` is the only bad one.
 * `imported_unverified` is neutral — it is the expected state of a fresh
 * import, not a fault.
 */
export function VerificationBadge({ state }: { state: string | null | undefined }) {
  if (!state) return null;
  const tone: BadgeTone =
    state === 'verified' ? 'good' : state === 'stale_disputed' ? 'bad' : 'neutral';
  const label = state === 'stale_disputed' ? 'disputed' : state.replace(/_/g, ' ');
  return <Badge tone={tone}>{label}</Badge>;
}

/* ── Stat tile ───────────────────────────────────────────────────────── */

export function StatTile({
  label, value, note, tone, icon: Icon,
}: {
  label: string;
  value: ReactNode;
  note?: string;
  /** `attn` marks a number needing action; `warn` marks a problem. */
  tone?: 'attn' | 'warn';
  icon?: LucideIcon;
}) {
  const cls = tone === 'attn' ? 'tile tile-attn' : tone === 'warn' ? 'tile tile-warn' : 'tile';
  return (
    <div className={cls}>
      <div className="tile-head">
        <div style={{ minWidth: 0 }}>
          <div className="tile-label">{label}</div>
          <div className="tile-value">{value}</div>
        </div>
        {Icon && (
          <div className="tile-icon" aria-hidden="true">
            <Icon size={18} strokeWidth={2.5} />
          </div>
        )}
      </div>
      {note && <div className="tile-note">{note}</div>}
    </div>
  );
}

/* ── Chart card ──────────────────────────────────────────────────────── */

export function ChartCard({
  title, subtitle, children, action,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <section className="chart-card">
      <div className="chart-head">
        <div style={{ minWidth: 0 }}>
          <div className="chart-title">{title}</div>
          {subtitle && <div className="chart-sub">{subtitle}</div>}
        </div>
        {action}
      </div>
      <div className="chart-body">{children}</div>
    </section>
  );
}

/* ── Empty state ─────────────────────────────────────────────────────── */

/**
 * An empty chart must say why it is empty. Most 1B/R2 series are legitimately
 * empty until the first send, and a bare "no data" reads as a bug.
 */
export function EmptyState({ title, description }: { title: string; description?: string }) {
  return (
    <div className="empty-state">
      <div className="empty-state-title">{title}</div>
      {description && <div className="empty-state-desc">{description}</div>}
    </div>
  );
}

/* ── Flash ───────────────────────────────────────────────────────────── */

export type FlashMessage = { text: string; err?: boolean } | null;

export function Flash({ message }: { message: FlashMessage }) {
  if (!message) return null;
  return <div className={message.err ? 'flash flash-err' : 'flash'}>{message.text}</div>;
}

/* ── Skeleton ────────────────────────────────────────────────────────── */

export function Skeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div aria-busy="true" aria-live="polite">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="skeleton skeleton-row" style={{ width: `${100 - i * 11}%` }} />
      ))}
    </div>
  );
}

/* ── Table ───────────────────────────────────────────────────────────── */

export interface Column<T> {
  key: string;
  header: string;
  /** Right-aligns and applies tabular figures. */
  numeric?: boolean;
  render: (row: T) => ReactNode;
}

export function DataTable<T>({
  columns, rows, empty, rowKey,
}: {
  columns: Column<T>[];
  rows: T[];
  empty: ReactNode;
  rowKey: (row: T, i: number) => string;
}) {
  if (!rows.length) return <>{empty}</>;
  return (
    <div className="table-wrap">
      <table className="data">
        <thead>
          <tr>
            {columns.map(c => (
              <th key={c.key} className={c.numeric ? 'num' : undefined}>{c.header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={rowKey(row, i)}>
              {columns.map(c => (
                <td key={c.key} className={c.numeric ? 'num' : undefined}>{c.render(row)}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
