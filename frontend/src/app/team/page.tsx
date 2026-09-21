/**
 * The people who built it.
 * Public on purpose, so the page can be opened from the login screen and
 * linked to without an account.
 */

import Link from 'next/link';

interface Member {
  name: string;
  role: string;
  blurb: string;
  /** Which of the four block colours the card gets. */
  tone: 'blue' | 'yellow' | 'ink' | 'paper';
}

const TEAM: Member[] = [
  {
    name: 'Alishbah Waheed',
    role: 'Frontend Developer',
    blurb: 'Builds candidate and company dashboards, challenge UI.',
    tone: 'blue',
  },
  {
    name: 'Uzair Siddiqui',
    role: 'Backend Developer',
    blurb: 'APIs, challenge management, submission pipeline.',
    tone: 'yellow',
  },
  {
    name: 'Qaseem',
    role: 'Algorithm Engineer',
    blurb: 'Implements ranking metrics: similarity, quality, readability, originality.',
    tone: 'ink',
  },
  {
    name: 'Nameera',
    role: 'Blockchain Developer',
    blurb: 'Cryptographic Skill Proof Chain, anonymous verified credentials.',
    tone: 'paper',
  },
  {
    name: 'Hanzala',
    role: 'Database Engineer',
    blurb: 'Schema design for submissions, rankings, and user data.',
    tone: 'yellow',
  },
  {
    name: 'Jaza',
    role: 'UI and UX Designer',
    blurb: 'Wireframes, user flows, visual design system.',
    tone: 'blue',
  },
  {
    name: 'Maroofa',
    role: 'Product Manager',
    blurb: 'Roadmap, sprint planning, feature prioritisation.',
    tone: 'paper',
  },
  {
    name: 'Warisha',
    role: 'QA Engineer',
    blurb: 'Test cases, bug tracking, submission pipeline validation.',
    tone: 'ink',
  },
  {
    name: 'Nawal Yasir',
    role: 'DevOps',
    blurb: 'Hosting, CI and CD pipeline, environment setup.',
    tone: 'blue',
  },
  {
    name: 'Uroob Naz',
    role: 'Docs and Research Lead',
    blurb: 'Reports, API documentation, presentation decks.',
    tone: 'yellow',
  },
];

export default function TeamPage() {
  return (
    <div className="page page-wide">
      <section className="team-hero">
        <div className="team-hero-tag">The people who built it</div>
        <h1 className="display">
          Ten people.<br />One <mark>ghost</mark> at a time.
        </h1>
        <p className="lede">
          GhostNet is a Design and Analysis of Algorithms project at the University
          of Karachi, UBIT. Every ranking algorithm behind it was written by hand,
          and every person below owns a piece of it.
        </p>
      </section>

      <div className="team-grid">
        {TEAM.map((m, i) => (
          <article key={m.name} className={`team-card tone-${m.tone}`}>
            <div className="team-num">{String(i + 1).padStart(2, '0')}</div>
            <div className="team-initials">{initials(m.name)}</div>
            <h2 className="team-name">{m.name}</h2>
            <div className="team-role">{m.role}</div>
            <p className="team-blurb">{m.blurb}</p>
          </article>
        ))}
      </div>

      <section className="card team-foot">
        <div className="row-between">
          <div>
            <div className="card-title">Want to see what they built?</div>
            <div className="card-meta">
              Post a problem, or answer one under a name nobody can trace.
            </div>
          </div>
          <Link href="/" className="btn btn-accent">Open GhostNet</Link>
        </div>
      </section>
    </div>
  );
}

function initials(name: string) {
  return name.split(/\s+/).slice(0, 2).map(w => w[0]).join('').toUpperCase();
}
