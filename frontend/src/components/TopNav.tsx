'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const LINKS = [
  { href: '/', label: 'Challenges' },
  { href: '/matching', label: 'Matches' },
  { href: '/schedule', label: 'Calendar' },
  { href: '/chain', label: 'Verified wins' },
];

export function TopNav() {
  const path = usePathname();

  return (
    <header className="topnav">
      <div className="topnav-inner">
        <Link href="/" className="brand">
          GhostNet<span>hiring based on what you can do</span>
        </Link>
        {LINKS.map(({ href, label }) => {
          const active = href === '/' ? path === '/' : path.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className="topnav-link"
              aria-current={active ? 'page' : undefined}
            >
              {label}
            </Link>
          );
        })}
      </div>
    </header>
  );
}
