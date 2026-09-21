'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { ensureGhost } from '../lib/ghost';

const LINKS = [
  { href: '/', label: 'Challenges' },
  { href: '/practice', label: 'Practice' },
  { href: '/inbox', label: 'Inbox' },
  { href: '/leaderboard', label: 'Leaderboard' },
  { href: '/me', label: 'My Ghost' },
];

export function TopNav() {
  const path = usePathname();
  const [name, setName] = useState('');

  // Every visitor gets a ghost the moment they arrive, so there is never a
  // sign up step between a person and their first entry.
  useEffect(() => {
    ensureGhost().then(g => setName(g.name)).catch(() => setName(''));
  }, []);

  return (
    <header className="topnav">
      <div className="topnav-inner">
        <Link href="/" className="brand">GhostNet</Link>
        <nav className="topnav-links">
          {LINKS.map(({ href, label }) => {
            const active = href === '/' ? path === '/' : path.startsWith(href);
            return (
              <Link key={href} href={href} className="topnav-link"
                aria-current={active ? 'page' : undefined}>
                {label}
                {href === '/me' && name ? <span className="topnav-me"> · {name}</span> : null}
              </Link>
            );
          })}
        </nav>
        <Link href="/post" className="btn btn-accent btn-sm">Post a challenge</Link>
      </div>
    </header>
  );
}
