'use client';

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
      <section className="card">
        <h1 className="page-title">Verified wins</h1>
        <div className="card-meta">
          Every win is recorded and linked to the one before it. Nobody can edit an old
          win without it showing.
        </div>
      </section>

      <Flash message={flash} />

      <div className="tile-grid">
        <StatTile label="Verified wins" value={blocks?.length ?? 0} />
        <StatTile label="Record" value={root ? root.slice(0, 10) + '…' : '—'} note="fingerprint of every win" />
      </div>

      {blocks !== null && blocks.length === 0 && (
        <div className="card">
          <EmptyState title="No wins yet" description="Rank a challenge and reveal its winner." />
        </div>
      )}

      {(blocks ?? []).map(b => (
        <section key={b.index} className="card">
          <div className="row-between">
            <div className="card-title">{b.record}</div>
            <span className="badge badge-good">Verified</span>
          </div>
          <div style={{ marginTop: 10 }}>
            <span className="algo-tag">Record id</span>
            <div className="hash">{b.hash}</div>
          </div>
          <div style={{ marginTop: 8 }}>
            <span className="algo-tag">Linked to</span>
            <div className="hash">{b.previous_hash}</div>
          </div>
        </section>
      ))}
    </div>
  );
}
