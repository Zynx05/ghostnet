'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import { saveSession } from '../../lib/auth';
import { Flash, type FlashMessage } from '../../components/ui';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [flash, setFlash] = useState<FlashMessage>(null);
  const [busy, setBusy] = useState(false);

  async function go() {
    setBusy(true);
    try {
      const s = await api.login(email, password);
      saveSession(s);
      router.push(s.role === 'company' ? '/company' : '/');
    } catch (e) {
      setFlash({ text: (e as Error).message, err: true });
      setBusy(false);
    }
  }

  return (
    <div className="page page-narrow">
      <section className="card auth-card">
        <h1 className="page-title">Welcome back</h1>
        <div className="card-meta">Same door for candidates and companies.</div>
        <Flash message={flash} />
        <form onSubmit={e => { e.preventDefault(); go(); }}>
          <div className="field">
            <label className="field-label">Email</label>
            <input className="field-input" type="email" value={email} autoComplete="email"
              onChange={e => setEmail(e.target.value)} autoFocus />
          </div>
          <div className="field">
            <label className="field-label">Password</label>
            <input className="field-input" type="password" value={password} autoComplete="current-password"
              onChange={e => setPassword(e.target.value)} />
          </div>
          <div className="actions">
            <button className="btn btn-accent btn-wide" disabled={busy}>{busy ? 'Logging in…' : 'Log in'}</button>
          </div>
        </form>
        <div className="card-meta auth-foot">
          New here? <Link href="/signup" className="link">Create an account</Link>
        </div>
      </section>

      <section className="card demo-card">
        <div className="card-title">Demo accounts</div>
        <div className="card-meta">Every password is <code>demo1234</code>.</div>
        <div className="demo-grid">
          <div><span className="algo-tag">Candidate</span>bilal@demo.pk</div>
          <div><span className="algo-tag">Candidate, stays masked</span>farhan@demo.pk</div>
          <div><span className="algo-tag">Company, Rs 10,000</span>northwind@demo.pk</div>
          <div><span className="algo-tag">Company, Rs 0</span>meridian@demo.pk</div>
        </div>
      </section>
    </div>
  );
}
