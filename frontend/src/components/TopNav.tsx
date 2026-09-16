'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

// Two tabs only. /matching and /schedule still exist and still work, they are
// just not part of the product a normal user needs to see.
const LINKS = [
  { href: '/', label: 'Challenges' },
  { href: '/chain', label: 'Skill Proof' },
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
