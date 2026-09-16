import type { Metadata } from 'next';
import './globals.css';
import './components.css';
import './ghostnet.css';
import { Sidebar } from '../components/Sidebar';

export const metadata: Metadata = {
  title: 'GhostNet',
  description: 'Hiring based on what you can do, not who you are.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        {/* Host Grotesk carries the headings, Space Mono carries every number,
            which keeps the score columns lined up. */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Host+Grotesk:ital,wght@0,300..800;1,300..800&family=Space+Mono:ital,wght@0,400;0,700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div className="shell">
          <Sidebar />
          <div className="shell-main">{children}</div>
        </div>
      </body>
    </html>
  );
}
