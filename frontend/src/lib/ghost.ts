/**
 * Who you are, without a login.
 *
 * The first time this browser needs an identity it asks the API for a ghost
 * and keeps the answer in localStorage. From then on that token is you. Clear
 * the browser and you are a new ghost, which is the honest trade for having
 * no passwords and no email addresses anywhere in the system.
 */

const KEY = 'ghostnet.ghost';
const BASE = process.env.NEXT_PUBLIC_API ?? 'http://localhost:8000';

export interface Ghost {
  ghost_id: string;
  name: string;
  token: string;
}

export function readGhost(): Ghost | null {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? (JSON.parse(raw) as Ghost) : null;
  } catch {
    return null;
  }
}

export async function ensureGhost(): Promise<Ghost> {
  const have = readGhost();
  if (have) return have;
  const res = await fetch(BASE + '/ghosts', { method: 'POST' });
  if (!res.ok) throw new Error('could not create a ghost');
  const ghost = (await res.json()) as Ghost;
  try {
    localStorage.setItem(KEY, JSON.stringify(ghost));
  } catch {
    // Private windows can refuse storage. The ghost still works for this page.
  }
  return ghost;
}

export function forgetGhost() {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // nothing to forget
  }
}
