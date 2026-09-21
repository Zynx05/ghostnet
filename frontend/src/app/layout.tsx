import type { Metadata } from 'next';
import './ghostnet.css';
import { TopNav } from '../components/TopNav';

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
        <TopNav />
        <main>{children}</main>
      </body>
    </html>
  );
}
