import test from 'node:test';
import assert from 'node:assert/strict';
import { eventKeys, answerKeys } from '../src/logic.js';

test('eventos válidos geram contadores sem dado pessoal', () => {
  assert.deepEqual(eventKeys({ e: 'start', s: 'whatsapp' }, '2026-09-30'), ['ev:start', 'ev:start:2026-09-30', 'src:whatsapp']);
  assert.deepEqual(eventKeys({ e: 'start', s: 'qualquer' }, 'd'), ['ev:start', 'ev:start:d', 'src:outro']);
  assert.deepEqual(eventKeys({ e: 'q', i: 3 }, 'd'), ['ev:q', 'ev:q:d', 'ev:q:3']);
});

test('eventos inválidos são rejeitados', () => {
  for (const b of [null, {}, { e: 'x' }, { e: 'q' }, { e: 'q', i: -1 }, { e: 'q', i: 1.5 }, { e: 'q', i: 1000 }]) assert.equal(eventKeys(b, 'd'), null);
});

test('respostas só aceitam ids e escolhas conhecidos', () => {
  assert.deepEqual(answerKeys({ a: { p_jornada: 'a', p_renda: 'info' }, l: ['lula'] }, 'd'),
    ['ans:envios', 'ans:envios:d', 'ans:p_jornada:a', 'ans:p_renda:info', 'lider:lula']);
  assert.deepEqual(answerKeys({ a: { p_x: 'b' }, l: ['lula', 'renan'] }, 'd').at(-1), 'lider:empate');
  for (const b of [{}, { a: {} }, { a: { 'x;drop': 'a' } }, { a: { p_x: 'c' } }, { a: { p_x: 'a' }, l: 'lula' }, { a: { p_x: 'a' }, l: ['<script>'] }]) assert.equal(answerKeys(b, 'd'), null);
});
