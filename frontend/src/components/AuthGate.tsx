'use client';

/**
 * Nothing is public. A visitor without a session is sent to the login page,
 * and the only pages that render without one are login and signup themselves.
 */

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, type ReactNode } from 'react';
import { useSession } from '../lib/auth';

const OPEN = ['/login', '/signup'];

export function AuthGate({ children }: { children: ReactNode }) {
  const session = useSession();
  const path = usePathname();
  const router = useRouter();
  const open = OPEN.includes(path);

  useEffect(() => {
    if (session === null && !open) router.replace('/login');
    if (session && open) router.replace(session.role === 'company' ? '/company' : '/');
  }, [session, open, router]);

  // Still finding out, or about to redirect. A blank beat beats a flash of the wrong page.
  if (session === undefined) return null;
  if (session === null && !open) return null;
  if (session && open) return null;

  return <>{children}</>;
}
