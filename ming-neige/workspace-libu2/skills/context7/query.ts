#!/usr/bin/env node

/**
 * Context7 Query CLI
 * 
 * Usage:
 *   npx tsx query.ts search <library_name> <query>
 *   npx tsx query.ts context <owner/repo> <query>
 */

import { config } from 'dotenv';
import { resolve } from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load .env from skill directory
config({ path: resolve(__dirname, '.env') });

const API_BASE = 'https://context7.com/api/v2';

async function searchLibrary(libraryName: string, query: string) {
  const apiKey = process.env.CONTEXT7_API_KEY;
  if (!apiKey) {
    console.error('Error: CONTEXT7_API_KEY not set in .env');
    process.exit(1);
  }

  const url = new URL(`${API_BASE}/libs/search`);
  url.searchParams.set('libraryName', libraryName);
  url.searchParams.set('query', query);

  try {
    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    console.log(JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Search failed:', error);
    process.exit(1);
  }
}

async function getContext(libraryId: string, query: string, type: string = 'txt') {
  const apiKey = process.env.CONTEXT7_API_KEY;
  if (!apiKey) {
    console.error('Error: CONTEXT7_API_KEY not set in .env');
    process.exit(1);
  }

  const url = new URL(`${API_BASE}/context`);
  url.searchParams.set('libraryId', libraryId);
  url.searchParams.set('query', query);
  url.searchParams.set('type', type);

  try {
    const response = await fetch(url.toString(), {
      headers: {
        'Authorization': `Bearer ${apiKey}`,
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const data = type === 'json' ? await response.json() : await response.text();
    console.log(typeof data === 'string' ? data : JSON.stringify(data, null, 2));
  } catch (error) {
    console.error('Context fetch failed:', error);
    process.exit(1);
  }
}

// CLI
const [,, command, ...args] = process.argv;

if (command === 'search' && args.length >= 2) {
  searchLibrary(args[0], args.slice(1).join(' '));
} else if (command === 'context' && args.length >= 2) {
  getContext(args[0], args.slice(1).join(' '));
} else {
  console.log(`
Context7 Query CLI

Usage:
  npx tsx query.ts search <library_name> <query>
  npx tsx query.ts context <owner/repo> <query>

Examples:
  npx tsx query.ts search "nextjs" "setup ssr"
  npx tsx query.ts context "vercel/next.js" "setup ssr"
  `);
  process.exit(1);
}
