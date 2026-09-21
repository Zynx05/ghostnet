/**
 * The shapes the API sends back.
 * These mirror the Pydantic models in the backend, so a change on one side
 * shows up as a red line on the other side instead of a blank screen.
 */

export interface Challenge {
  id: number;
  company_id: number | null;
  title: string;
  company: string;
  statement: string;
  reward: string;
  start_day: number;
  end_day: number;
  revealed: boolean;
  practice: boolean;
  entries?: number;
  created_at?: string;
}

export interface Submission {
  id: number;
  ghost_id: string;
  ghost_name: string;
  content: string;
}

export interface RankedRow {
  ghost_id: string;
  ghost_name: string;
  relevance: number;
  quality: number;
  structure: number;
  cyclomatic: number;
  plagiarism: number;
  longest_copied: string;
  final_score: number;
  rank: number;
}

export interface RankResponse {
  weights: Record<string, number>;
  results: RankedRow[];
}

export interface ProofStep {
  hash: string;
  side: 'left' | 'right';
}

export interface RevealResponse {
  winner: RankedRow;
  merkle_root: string;
  leaf: string;
  proof: ProofStep[];
  leaf_count: number;
}

export interface UnmaskResponse {
  ghost_id: string;
  masked: boolean;
  real_name: string;
  charged_pkr: number;
  balance_pkr?: number;
}

export interface PracticeResult {
  would_rank: number;
  out_of: number;
  scores: RankedRow;
}

export interface Message {
  id: number;
  kind: 'tap' | 'whisper' | 'answer';
  body: string;
  created_at: string;
  challenge_id: number;
  title: string;
  company: string;
}

export interface Question {
  id: number;
  ghost_id: string;
  ghost_name: string;
  question: string;
  answer: string;
}

export interface MyEntry {
  challenge_id: number;
  title: string;
  company: string;
  revealed: boolean;
  ghost_id: string;
  rank: number | null;
  final_score: number | null;
}

export interface MyPractice {
  challenge_id: number;
  title: string;
  would_rank: number;
  out_of: number;
  final_score: number;
}

export interface MyPage {
  ghost: { ghost_id: string; name: string; real_name: string };
  entries: MyEntry[];
  practice: MyPractice[];
  proofs: (MyEntry & { seal: string })[];
  check_code: string;
}

export interface LeaderRow {
  ghost_id: string;
  name: string;
  entries: number;
  wins: number;
}

export interface ChainBlock {
  index: number;
  record: string;
  previous_hash: string;
  hash: string;
  ghost_id: string;
  ghost_name: string;
  title: string;
  company: string;
  score: number;
}

export interface Window {
  id?: number;
  title: string;
  start: number;
  end: number;
}

export interface ScheduleResponse {
  sorted_by_finish: Window[];
  chosen: Window[];
  dropped: Window[];
}

export interface MatchResponse {
  pairs: { company: string; candidate: string }[];
  log: string[];
}
