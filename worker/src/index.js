import { day, eventKeys, answerKeys } from './logic.js';

const ALLOWED = ['https://planos2026.com.br', 'https://www.planos2026.com.br', 'https://drapala.github.io'];

function cors(origin) {
  const allow = ALLOWED.includes(origin) ? origin : ALLOWED[0];
  return { 'Access-Control-Allow-Origin': allow, 'Access-Control-Allow-Methods': 'POST, GET, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Vary': 'Origin' };
}

async function bump(db, keys) {
  const stmt = db.prepare('INSERT INTO counts (k, n) VALUES (?1, 1) ON CONFLICT(k) DO UPDATE SET n = n + 1');
  await db.batch(keys.map(k => stmt.bind(k)));
}

async function readBody(request) {
  const text = await request.text();
  if (text.length > 4000) return null;
  try { return JSON.parse(text); } catch { return null; }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const headers = cors(request.headers.get('Origin') || '');
    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers });
    if (request.method === 'POST' && (url.pathname === '/e' || url.pathname === '/r')) {
      const body = await readBody(request);
      const keys = url.pathname === '/e' ? eventKeys(body, day()) : answerKeys(body, day());
      if (!keys) return new Response('invalid', { status: 400, headers });
      await bump(env.DB, keys);
      return new Response(null, { status: 204, headers });
    }
    if (request.method === 'GET' && url.pathname === '/stats') {
      if (!env.STATS_TOKEN || url.searchParams.get('token') !== env.STATS_TOKEN) return new Response('forbidden', { status: 403 });
      const { results } = await env.DB.prepare('SELECT k, n FROM counts ORDER BY k').all();
      return Response.json(Object.fromEntries(results.map(r => [r.k, r.n])));
    }
    return new Response('not found', { status: 404, headers });
  },
};
