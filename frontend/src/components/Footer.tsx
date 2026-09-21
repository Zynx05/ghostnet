import Link from 'next/link';

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <div>
          <div className="footer-brand">GhostNet</div>
          <div className="footer-note">
            Hiring based on what you can do, not who you are.
          </div>
          <div className="footer-note footer-sub">
            Design and Analysis of Algorithms · University of Karachi, UBIT
          </div>
        </div>
        <Link href="/team" className="team-btn">
          <span className="team-btn-label">Meet the</span>
          <span className="team-btn-main">Development Team</span>
          <span className="team-btn-arrow" aria-hidden="true">→</span>
        </Link>
      </div>
    </footer>
  );
}
