'use client';

/**
 * Member 7  Blockchain Developer.
 * Every revealed win, linked block by block. Each block carries the hash of the
 * one before it, so editing an old win breaks every hash that follows.
 */

import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import type { ChainBlock } from '../../lib/types';
import { EmptyState, Flash, StatTile, type FlashMessage } from '../../components/ui';

export default function ChainPage() {
  const [blocks, setBlocks] = useState<ChainBlock[] | null>(null);
  const [root, setRoot] = useState('');
  const [flash, setFlash] = useState<FlashMessage>(null);

  useEffect(() => {
    api.chain()
      .then(d => { setBlocks(d.blocks); setRoot(d.merkle_root); })
      .catch(e => setFlash({ text: e.message, err: true }));
  }, []);

  return (
    <div className="page">
      <h1 className="page-title">Skill Proof chain</h1>
      <p className="page-subtitle">
        A profile is not a list of universities. It is this chain, and every
        block in it was earned by winning a challenge under a ghost name.
      </p>

      <Flash message={flash} />

      <div className="tile-grid">
        <StatTile label="Verified wins" value={blocks?.length ?? 0} />
        <StatTile label="Hash function" value="SHA 256" note="64 hex characters" />
        <StatTile label="Proof size" value="O(log n)" note="siblings on the path" />
      </div>

      {blocks !== null && blocks.length === 0 && (
        <EmptyState
          title="The chain is empty"
          description="Rank a challenge and reveal its winner, then come back here."
        />
      )}

      {root && (
        <section className="card">
          <div className="card-title">Merkle root over every win</div>
          <div className="hash" style={{ marginTop: '0.4rem' }}>{root}</div>
          <div className="card-meta" style={{ marginTop: '0.5rem' }}>
            One value that stands for the whole list. Change any win and this changes.
          </div>
        </section>
      )}

      <div className="stack">
        {(blocks ?? []).map(b => (
          <section key={b.index} className="card">
            <div className="row-between">
              <div className="card-title">Block {b.index}</div>
              <span className="owner">sha 256</span>
            </div>
            <p style={{ marginTop: '0.4rem' }}>{b.record}</p>
            <div style={{ marginTop: '0.6rem' }}>
              <span className="algo-tag">previous hash</span>
              <div className="hash">{b.previous_hash}</div>
            </div>
            <div style={{ marginTop: '0.5rem' }}>
              <span className="algo-tag">this block hash</span>
              <div className="hash">{b.hash}</div>
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
