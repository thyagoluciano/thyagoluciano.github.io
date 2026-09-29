#!/usr/bin/env bash
# Publica no site: exporta o vault, valida o build, faz commit e push (SPEC seção 7).
set -euo pipefail
cd "$(dirname "$0")/.."

resumo="$(mktemp)"
trap 'rm -f "$resumo"' EXIT

echo "1/5 Exportando o vault (modo estrito)…"
uv run tools/exportar.py --estrito --saida-json "$resumo"

echo "2/5 Gerando o site para validar…"
npx quartz build

echo "3/5 Preparando o commit…"
git add content tools/manifesto.json

if git diff --cached --quiet; then
  echo "Nada novo para publicar."
  exit 0
fi

titulos="$(python3 - "$resumo" <<'PY'
import json, sys
dados = json.load(open(sys.argv[1], encoding="utf-8"))
titulos = [n["titulo"] for n in dados["novas"] + dados["alteradas"]]
print(", ".join(titulos) if titulos else "atualiza o site")
PY
)"

echo "4/5 Commit: Publica: ${titulos}"
git commit -m "Publica: ${titulos}"

echo "5/5 Enviando para o GitHub…"
git push origin main

echo "Pronto. O deploy roda no GitHub Actions (aba Actions do repositório)."
