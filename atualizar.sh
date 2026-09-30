#!/bin/sh
set -e
cd "$(dirname "$0")"
python3 ~/planos-anonimos/_trabalho/build_quiz.py
cp ~/planos-anonimos/quiz_planos_2026.html site/index.html
git add site/index.html && git commit -m "Atualiza o quiz" && git push
