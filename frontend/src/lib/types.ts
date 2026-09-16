/**
 * The shapes the API sends back.
 * These mirror the Pydantic models in the backend, so a change on one side
 * shows up as a red line on the other side instead of a blank screen.
 */

export interface Challenge {
  id: number;
  title: string;
  company: string;
  statement: string;
  reward: string;
  start_day: number;
  end_day: number;
  revealed: boolean;
  created_at?: string;
}

export interface Submission {
  id: number;
  ghost_id: string;
  content: string;
}

export interface RankedRow {
  ghost_id: string;
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
  /** Null until the company presses reveal. Anonymity lives in the type too. */
  real_name: string;
  merkle_root: string;
  leaf: string;
  proof: ProofStep[];
  leaf_count: number;
}

export interface ChainBlock {
  index: number;
  record: string;
  previous_hash: string;
  hash: string;
  ghost_id: string;
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
