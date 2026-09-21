'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { api } from '../lib/api';
import { clearSession, saveSession, useSession } from '../lib/auth';

const CANDIDATE = [
  { href: '/', label: 'Challenges' },
  { href: '/practice', label: 'Practice' },
  { href: '/inbox', label: 'Inbox' },
  { href: '/leaderboard', label: 'Leaderboard' },
  { href: '/me', label: 'My Ghost' },
];

const COMPANY = [
  { href: '/', label: 'Challenges' },
  { href: '/company', label: 'My challenges' },
  { href: '/leaderboard', label: 'Leaderboard' },
];

const GUEST = [
  { href: '/', label: 'Challenges' },
  { href: '/leaderboard', label: 'Leaderboard' },
];

export function TopNav() {
  const path = usePathname();
  const router = useRouter();
  const session = useSession();

  // Refresh the name and balance from the server once per page load, so a
  // topup or an unmask made in another tab shows here without a reload.
  useEffect(() => {
    if (!session) return;
    api.session().then(saveSession).catch(() => clearSession());
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session?.token]);

  const links = session?.role === 'candidate' ? CANDIDATE : session?.role === 'company' ? COMPANY : GUEST;

  async function logout() {
    try { await api.logout(); } catch { /* the token may already be gone */ }
    clearSession();
    router.push('/');
  }

  return (
    <header className="topnav">
      <div className="topnav-inner">
        <Link href="/" className="brand">GhostNet</Link>
        <nav className="topnav-links">
          {links.map(({ href, label }) => {
            const active = href === '/' ? path === '/' : path.startsWith(href);
            return (
              <Link key={href} href={href} className="topnav-link" aria-current={active ? 'page' : undefined}>
                {label}
              </Link>
            );
          })}
        </nav>

        {!session ? null : session.role === 'company' ? (
          <div className="topnav-right">
            <span className="chip" title="Balance">Rs {session.balance_pkr.toLocaleString()}</span>
            <Link href="/post" className="btn btn-sm btn-accent">Post a challenge</Link>
            <button className="btn btn-sm btn-ghost" onClick={logout}>Log out</button>
          </div>
        ) : (
          <div className="topnav-right">
            <span className="chip">{session.name}</span>
            <button className="btn btn-sm btn-ghost" onClick={logout}>Log out</button>
          </div>
        )}
      </div>
    </header>
  );
}
