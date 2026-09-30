export const EVENTS = new Set(['start', 'q', 'done', 'copy']);
export const SOURCES = new Set(['whatsapp', 'instagram', 'facebook', 'x', 'tiktok', 'google', 'direto', 'outro']);
export const CHOICES = new Set(['a', 'b', 'undecided', 'info']);
const ITEM = /^p_[a-z0-9_]{1,40}$/;
const CANDIDATE = /^[a-z]{2,20}$/;

export function day(now = new Date()) {
  return now.toISOString().slice(0, 10);
}

export function eventKeys(body, today) {
  if (!body || typeof body !== 'object' || !EVENTS.has(body.e)) return null;
  const keys = [`ev:${body.e}`, `ev:${body.e}:${today}`];
  if (body.e === 'q') {
    if (!Number.isInteger(body.i) || body.i < 0 || body.i > 99) return null;
    keys.push(`ev:q:${body.i}`);
  }
  if (body.e === 'start') {
    const source = SOURCES.has(body.s) ? body.s : 'outro';
    keys.push(`src:${source}`);
  }
  return keys;
}

export function answerKeys(body, today) {
  if (!body || typeof body !== 'object' || !body.a || typeof body.a !== 'object') return null;
  const entries = Object.entries(body.a);
  if (entries.length === 0 || entries.length > 60) return null;
  const keys = ['ans:envios', `ans:envios:${today}`];
  for (const [item, choice] of entries) {
    if (!ITEM.test(item) || !CHOICES.has(choice)) return null;
    keys.push(`ans:${item}:${choice}`);
  }
  if (body.l !== undefined) {
    if (!Array.isArray(body.l) || body.l.length > 5 || !body.l.every(k => CANDIDATE.test(k))) return null;
    keys.push(body.l.length === 1 ? `lider:${body.l[0]}` : `lider:empate`);
  }
  return keys;
}
