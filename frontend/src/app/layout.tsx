import type { Metadata } from 'next';
import './ghostnet.css';
import { TopNav } from '../components/TopNav';
import { Footer } from '../components/Footer';
import { AuthGate } from '../components/AuthGate';

export const metadata: Metadata = {
  title: 'GhostNet',
  description: 'Hiring based on what you can do, not who you are.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div className="shell">
          <TopNav />
          <main><AuthGate>{children}</AuthGate></main>
          <Footer />
        </div>
      </body>
    </html>
  );
}
