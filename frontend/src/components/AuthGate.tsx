'use client';

/**
 * Nothing is public. A visitor without a session is sent to the login page,
 * and the only pages that render without one are login and signup themselves.
 */

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, type ReactNode } from 'react';
import { useSession } from '../lib/auth';

// The team page is public, so it can be opened from the login screen.
const OPEN = ['/login', '/signup', '/team'];

export function AuthGate({ children }: { children: ReactNode }) {
  const session = useSession();
  const path = usePathname();
  const router = useRouter();
  const open = OPEN.includes(path);

  useEffect(() => {
    if (session === null && !open) router.replace('/login');
    // A logged in visitor is bounced off login and signup, but the team
    // page is for everybody, so it is left alone.
    if (session && open && path !== '/team') {
      router.replace(session.role === 'company' ? '/company' : '/');
    }
  }, [session, open, router]);

  // Still finding out, or about to redirect. A blank beat beats a flash of the wrong page.
  if (session === undefined) return null;
  if (session === null && !open) return null;
  if (session && open && path !== '/team') return null;

  return <>{children}</>;
}
