'use client';

import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import type { ChainBlock } from '../../lib/types';
import { EmptyState, Flash, type FlashMessage } from '../../components/ui';

export default function ChainPage() {
  const [blocks, setBlocks] = useState<ChainBlock[] | null>(null);
  const [holders, setHolders] = useState<string[]>([]);
  const [root, setRoot] = useState('');
  const [who, setWho] = useState<string>('');
  const [flash, setFlash] = useState<FlashMessage>(null);

  useEffect(() => {
    api.chain()
      .then(d => {
        setBlocks(d.blocks);
        setHolders(d.holders);
        setRoot(d.merkle_root);
        setWho(d.holders[0] ?? '');
      })
      .catch(e => setFlash({ text: e.message, err: true }));
  }, []);

  const mine = (blocks ?? []).filter(b => b.ghost_id === who);

  return (
    <div className="page">
      <section className="card">
        <h1 className="page-title">Skill Proof Chain</h1>
        <div className="card-meta">
          A CV says where you have been. This says what you have done, and an
          employer can check it without ever learning your name.
        </div>
      </section>

      <Flash message={flash} />

      {blocks !== null && blocks.length === 0 && (
        <div className="card">
          <EmptyState
            title="No proofs yet"
            description="Win a challenge and your first proof appears here."
          />
        </div>
      )}

      {holders.length > 0 && (
        <>
          {holders.length > 1 && (
            <div className="cluster">
              {holders.map(h => (
                <button
                  key={h}
                  className={h === who ? 'btn btn-accent' : 'btn'}
                  onClick={() => setWho(h)}
                >
                  {h}
                </button>
              ))}
            </div>
          )}

          {/* The credential itself. Identity is the ghost id and nothing more. */}
          <section className="credential">
            <div className="credential-head">
              <div>
                <span className="algo-tag">Skill Proof holder</span>
                <div className="credential-id">{who}</div>
              </div>
              <div className="credential-count">
                <div className="credential-count-n">{mine.length}</div>
                <div className="algo-tag">verified {mine.length === 1 ? 'win' : 'wins'}</div>
              </div>
            </div>
            <div className="credential-foot">
              <span className="algo-tag">Check code</span>
              <div className="hash">{root}</div>
            </div>
          </section>

          <section className="card">
            <div className="card-title">What this person has proven</div>
            <div className="card-meta">
              Each win is sealed to the one before it. Change an old win and every
              seal after it stops matching, so the record cannot be quietly rewritten.
            </div>

            <div className="chain">
              {mine.map((b, i) => (
                <div key={b.index} className="chain-item">
                  <div className="chain-rail">
                    <div className="chain-dot">✓</div>
                    {i < mine.length - 1 && <div className="chain-line" />}
                  </div>
                  <div className="chain-body">
                    <div className="chain-title">{b.title}</div>
                    <div className="card-meta">{b.company}</div>
                    <div className="chain-seal">
                      <span className="algo-tag">Seal</span>
                      <div className="hash">{b.hash.slice(0, 32)}…</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section className="card">
            <div className="card-title">How an employer checks this</div>
            <ol className="steps">
              <li>They are given the check code above and the win being claimed.</li>
              <li>They recompute the seal from that win alone.</li>
              <li>If it matches the check code, the win is real.</li>
            </ol>
            <div className="card-meta" style={{ marginTop: 10 }}>
              They never see the other candidates, and they never see a name until
              the holder chooses to share one.
            </div>
          </section>
        </>
      )}
    </div>
  );
}
