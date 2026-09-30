#!/bin/sh
set -e
cd "$(dirname "$0")"
QUIZ_TELEMETRY_URL=https://planos2026-telemetria.planos2026.workers.dev python3 ~/planos-anonimos/_trabalho/build_quiz.py
cp ~/planos-anonimos/quiz_planos_2026.html site/index.html
python3 ~/planos-anonimos/_trabalho/build_quiz.py >/dev/null
git add site/index.html && git commit -m "Atualiza o quiz" && git push
