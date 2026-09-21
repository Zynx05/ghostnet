/**
 * Every call to the FastAPI backend goes through this file.
 * One place to change the address, one place that handles an error, and one
 * place that attaches the session token so the server knows who is asking.
 */

import { readSession, type Session } from './auth';
import type {
  Challenge, Submission, RankResponse, RankedRow, RevealResponse, UnmaskResponse,
  PracticeResult, Message, Question, MyPage, LeaderRow,
  ChainBlock, ScheduleResponse, MatchResponse,
} from './types';

const BASE = process.env.NEXT_PUBLIC_API ?? 'http://localhost:8000';

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function call<T>(path: string, options?: RequestInit): Promise<T> {
  const session = readSession();
  const res = await fetch(BASE + path, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(session ? { 'X-Token': session.token } : {}),
      ...(options?.headers ?? {}),
    },
    cache: 'no-store',
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? 'request failed');
  }
  return res.json() as Promise<T>;
}

const post = (body: unknown = {}) => ({ method: 'POST', body: JSON.stringify(body) });

export const api = {
  // Accounts
  signup: (email: string, password: string, role: 'candidate' | 'company', company_name = '') =>
    call<Session>('/auth/signup', post({ email, password, role, company_name })),
  login: (email: string, password: string) => call<Session>('/auth/login', post({ email, password })),
  session: () => call<Session>('/auth/session'),
  logout: () => call<{ ok: true }>('/auth/logout', post()),

  // Challenges
  challenges: () => call<Challenge[]>('/challenges'),
  challenge: (id: number) => call<Challenge>(`/challenges/${id}`),
  createChallenge: (body: { title: string; statement: string; reward: string; start_day: number; end_day: number }) =>
    call<{ id: number }>('/challenges', post(body)),
  companyChallenges: () => call<Challenge[]>('/company/challenges'),
  topup: () => call<Session>('/company/topup', post()),

  // Entries
  submissions: (id: number) => call<Submission[]>(`/challenges/${id}/submissions`),
  submit: (id: number, content: string) =>
    call<{ ghost_id: string; ghost_name: string }>(`/challenges/${id}/submissions`, post({ content })),

  // Ranking, closing, unmasking
  rank: (id: number) => call<RankResponse>(`/challenges/${id}/rank`, post()),
  results: (id: number) => call<RankedRow[]>(`/challenges/${id}/results`),
  reveal: (id: number) => call<RevealResponse>(`/challenges/${id}/reveal`, post()),
  unmasks: (id: number) => call<Record<string, string>>(`/challenges/${id}/unmasks`),
  unmask: (id: number, ghost_id: string) => call<UnmaskResponse>(`/challenges/${id}/unmask`, post({ ghost_id })),

  // Practice
  practiceList: () => call<Challenge[]>('/practice'),
  practice: (id: number, content: string) => call<PracticeResult>(`/challenges/${id}/practice`, post({ content })),

  // Inbox and messages from companies
  inbox: () => call<Message[]>('/inbox'),
  message: (id: number, ghost_id: string, kind: 'tap' | 'whisper', body = '') =>
    call<{ ok: true }>(`/challenges/${id}/messages`, post({ ghost_id, kind, body })),

  // Questions on a challenge
  questions: (id: number) => call<Question[]>(`/challenges/${id}/questions`),
  ask: (id: number, question: string) => call<{ ok: true }>(`/challenges/${id}/questions`, post({ question })),
  answer: (questionId: number, answer: string) => call<{ ok: true }>(`/questions/${questionId}/answer`, post({ answer })),

  // Me
  me: () => call<MyPage>('/me'),
  setName: (real_name: string) => call<{ ok: true }>('/me', { method: 'PATCH', body: JSON.stringify({ real_name }) }),

  // Leaderboard and the proof chain
  leaderboard: () => call<LeaderRow[]>('/leaderboard'),
  chain: () => call<{ blocks: ChainBlock[]; merkle_root: string; holders: string[] }>('/chain'),

  // Side pages kept for the viva
  schedule: () => call<ScheduleResponse>('/schedule'),
  match: (candidates: Record<string, string[]>, companies: Record<string, string[]>) =>
    call<MatchResponse>('/match', post({ candidates, companies })),
};
