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
      <body>
        <TopNav />
        <main>{children}</main>
      </body>
    </html>
  );
}
