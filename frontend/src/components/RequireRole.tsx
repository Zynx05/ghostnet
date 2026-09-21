'use client';

/**
 * Wraps a page that only makes sense for one kind of account.
 * Shows a short card with the right links instead of a blank screen or an
 * error from the API.
 */

import Link from 'next/link';
import type { ReactNode } from 'react';
import { useSession, type Role } from '../lib/auth';
import { Skeleton } from './ui';

export function RequireRole({ role, children }: { role: Role; children: ReactNode }) {
  const session = useSession();

  if (session === undefined) {
    return <div className="page"><div className="card"><Skeleton rows={3} /></div></div>;
  }

  if (session === null) {
    return (
      <div className="page">
        <section className="card gate">
          <div className="card-title">Log in to continue</div>
          <div className="card-meta">
            {role === 'candidate'
              ? 'This page is yours. It needs to know which ghost you are.'
              : 'This page is for companies that post challenges.'}
          </div>
          <div className="actions" style={{ justifyContent: 'flex-start' }}>
            <Link href="/login" className="btn btn-accent">Log in</Link>
            <Link href="/signup" className="btn">Sign up</Link>
          </div>
        </section>
      </div>
    );
  }

  if (session.role !== role) {
    return (
      <div className="page">
        <section className="card gate">
          <div className="card-title">
            {role === 'candidate' ? 'This page is for candidates' : 'This page is for companies'}
          </div>
          <div className="card-meta">
            You are logged in as {session.role === 'company' ? 'the company ' + session.name : session.name}.
          </div>
          <div className="actions" style={{ justifyContent: 'flex-start' }}>
            <Link href="/" className="btn">Back to challenges</Link>
          </div>
        </section>
      </div>
    );
  }

  return <>{children}</>;
}
