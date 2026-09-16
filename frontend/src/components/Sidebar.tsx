'use client';

/**
 * Navigation. One entry per part of the demo, in the order it should be shown
 * to the examiner, so nobody has to remember where to click next.
 */

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Layers, Users, CalendarRange, Link2 } from 'lucide-react';

const LINKS = [
  { href: '/', label: 'Challenges', icon: Layers, note: 'rank submissions' },
  { href: '/matching', label: 'Matching', icon: Users, note: 'Gale Shapley' },
  { href: '/schedule', label: 'Schedule', icon: CalendarRange, note: 'greedy intervals' },
  { href: '/chain', label: 'Proof chain', icon: Link2, note: 'Merkle and SHA 256' },
];

export function Sidebar() {
  const path = usePathname();

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        GhostNet
        <div className="sidebar-brand-sub">skill first hiring</div>
      </div>

      <nav className="nav-group">
        {LINKS.map(({ href, label, icon: Icon, note }) => {
          const active = href === '/' ? path === '/' : path.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className="nav-link"
              aria-current={active ? 'page' : undefined}
            >
              <Icon size={16} strokeWidth={2.5} />
              <span className="nav-link-label">
                {label}
                <span className="nav-link-note">{note}</span>
              </span>
            </Link>
          );
        })}
      </nav>

      <div className="sidebar-foot">
        DAA Project
        <br />
        University of Karachi, UBIT
      </div>
    </aside>
  );
}
