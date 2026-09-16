/**
 * Every call to the FastAPI backend goes through this file.
 * One place to change the address, one place that handles an error.
 */

import type {
  Challenge, Submission, RankResponse, RevealResponse,
  ChainBlock, ScheduleResponse, MatchResponse,
} from './types';

const BASE = process.env.NEXT_PUBLIC_API ?? 'http://localhost:8000';

async function call<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    cache: 'no-store',
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(body.detail ?? 'request failed');
  }
  return res.json() as Promise<T>;
}

export const api = {
  challenges: () => call<Challenge[]>('/challenges'),

  challenge: (id: number) => call<Challenge>(`/challenges/${id}`),

  createChallenge: (body: Partial<Challenge>) =>
    call<{ id: number }>('/challenges', { method: 'POST', body: JSON.stringify(body) }),

  submissions: (id: number) => call<Submission[]>(`/challenges/${id}/submissions`),

  submit: (id: number, content: string, real_name: string) =>
    call<{ ghost_id: string }>(`/challenges/${id}/submissions`, {
      method: 'POST',
      body: JSON.stringify({ content, real_name }),
    }),

  rank: (id: number) => call<RankResponse>(`/challenges/${id}/rank`, { method: 'POST' }),

  reveal: (id: number) => call<RevealResponse>(`/challenges/${id}/reveal`, { method: 'POST' }),

  chain: () => call<{ blocks: ChainBlock[]; merkle_root: string }>('/chain'),

  schedule: () => call<ScheduleResponse>('/schedule'),

  match: (candidates: Record<string, string[]>, companies: Record<string, string[]>) =>
    call<MatchResponse>('/match', {
      method: 'POST',
      body: JSON.stringify({ candidates, companies }),
    }),
};
