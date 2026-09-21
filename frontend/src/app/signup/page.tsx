'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import { saveSession, type Role } from '../../lib/auth';
import { Flash, type FlashMessage } from '../../components/ui';

export default function SignupPage() {
  const router = useRouter();
  const [role, setRole] = useState<Role>('candidate');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [company, setCompany] = useState('');
  const [flash, setFlash] = useState<FlashMessage>(null);
  const [busy, setBusy] = useState(false);

  async function go() {
    setBusy(true);
    try {
      const s = await api.signup(email, password, role, company);
      saveSession(s);
      router.push(role === 'company' ? '/company' : '/me');
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
      setBusy(false);
    }
  }

  return (
    <div className="page page-narrow">
      <section className="card auth-card">
        <h1 className="page-title">Create an account</h1>

        <div className="role-switch" role="tablist">
          <button role="tab" aria-selected={role === 'candidate'} className={role === 'candidate' ? 'on' : ''}
            onClick={() => setRole('candidate')}>
            <strong>I want work</strong>
            <span>You get a ghost name. Nobody sees who you are unless you win.</span>
          </button>
          <button role="tab" aria-selected={role === 'company'} className={role === 'company' ? 'on' : ''}
            onClick={() => setRole('company')}>
            <strong>I am hiring</strong>
            <span>Post a real problem. Rank the answers. Pay only to unmask.</span>
          </button>
        </div>

        <Flash message={flash} />
        <form onSubmit={e => { e.preventDefault(); go(); }}>
          {role === 'company' && (
            <div className="field">
              <label className="field-label">Company name</label>
              <input className="field-input" value={company} onChange={e => setCompany(e.target.value)} autoFocus />
            </div>
          )}
          <div className="field">
            <label className="field-label">Email</label>
            <input className="field-input" type="email" value={email} autoComplete="email"
              onChange={e => setEmail(e.target.value)} autoFocus={role === 'candidate'} />
          </div>
          <div className="field">
            <label className="field-label">Password</label>
            <input className="field-input" type="password" value={password} autoComplete="new-password"
              onChange={e => setPassword(e.target.value)} />
            <div className="field-hint">At least six characters.</div>
          </div>
          <div className="actions">
            <button className="btn btn-accent btn-wide" disabled={busy}>
              {busy ? 'Creating…' : role === 'candidate' ? 'Get my ghost' : 'Create company'}
            </button>
          </div>
        </form>
        <div className="card-meta auth-foot">
          Already have one? <Link href="/login" className="link">Log in</Link>
        </div>
      </section>
    </div>
  );
}
