'use client';

/**
 * One conversation, drawn as bubbles.
 * Used by the candidate inbox and by the company on its own challenge page,
 * so the two sides never drift apart. `mine` says which side is on the right.
 */

import { useState } from 'react';
import type { Thread as ThreadType } from '../lib/types';

const KIND_LABEL: Record<string, string> = {
  tap: 'Wants to talk',
  whisper: 'Feedback',
  answer: 'Answered your question',
};

export function Bubbles({ thread, mine }: { thread: ThreadType; mine: 'company' | 'ghost' }) {
  return (
    <div className="bubbles">
      {thread.messages.map(m => {
        const isMine = m.sender === mine;
        const label = KIND_LABEL[m.kind];
        return (
          <div key={m.id} className={isMine ? 'bubble-row bubble-row-mine' : 'bubble-row'}>
            <div className={isMine ? 'bubble bubble-mine' : 'bubble'}>
              {label && !isMine && <span className="bubble-kind">{label}</span>}
              <div className="bubble-body">{m.body}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function Composer({
  onSend, placeholder = 'Write a reply',
}: {
  onSend: (text: string) => Promise<void> | void;
  placeholder?: string;
}) {
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);

  async function send() {
    if (!text.trim() || busy) return;
    setBusy(true);
    try {
      await onSend(text.trim());
      setText('');
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="composer">
      <input
        className="field-input"
        value={text}
        placeholder={placeholder}
        onChange={e => setText(e.target.value)}
        onKeyDown={e => e.key === 'Enter' && send()}
      />
      <button className="btn btn-accent" onClick={send} disabled={busy || !text.trim()}>
        Send →
      </button>
    </div>
  );
}
