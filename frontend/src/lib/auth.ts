/**
 * Who is logged in.
 *
 * The API hands back a session on signup or login. The browser keeps it in
 * localStorage and sends its token on every request. There is one session
 * shape for both roles, so the nav can be drawn without a second call.
 */

import { useEffect, useState } from 'react';

const KEY = 'ghostnet.session';

export type Role = 'candidate' | 'company';

export interface Session {
  token: string;
  user_id: number;
  role: Role;
  email: string;
  /** Ghost name for a candidate, company name for a company. */
  name: string;
  balance_pkr: number;
  ghost_id: string;
}

export function readSession(): Session | null {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Session) : null;
  } catch {
    return null;
  }
}

export function saveSession(s: Session) {
  try {
    localStorage.setItem(KEY, JSON.stringify(s));
  } catch {
    // Private windows can refuse storage. The session still works for this page.
  }
  window.dispatchEvent(new Event('ghostnet:session'));
}

export function clearSession() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // nothing to clear
  }
  window.dispatchEvent(new Event('ghostnet:session'));
}

/**
 * undefined while the page is still finding out, null when logged out,
 * a Session when logged in. Re-renders when the session changes anywhere.
 */
export function useSession(): Session | null | undefined {
  const [session, setSession] = useState<Session | null | undefined>(undefined);
  useEffect(() => {
    const read = () => setSession(readSession());
    read();
    window.addEventListener('ghostnet:session', read);
    window.addEventListener('storage', read);
    return () => {
      window.removeEventListener('ghostnet:session', read);
      window.removeEventListener('storage', read);
    };
  }, []);
  return session;
}
