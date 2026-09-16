import path from 'node:path';
import type { NextConfig } from 'next';

const config: NextConfig = {
  // There is a lockfile here and another one at the project root, so Next has
  // to be told which folder is the frontend. Without this it prints a warning
  // on every start and guesses.
  outputFileTracingRoot: path.join(process.cwd()),
};

export default config;
