#!/usr/bin/env bash

set -euo pipefail

TRANSLATE_SCRIPT="translate.py"
OUTPUT_DIR="translations/it"

mkdir -p "$OUTPUT_DIR"

if [[ ! -f "$TRANSLATE_SCRIPT" ]]; then
  echo "Errore: non trovo $TRANSLATE_SCRIPT nella cartella corrente."
  exit 1
fi

shopt -s nullglob

notebooks=(*.ipynb)

if (( ${#notebooks[@]} == 0 )); then
  echo "Nessun file .ipynb trovato nella cartella corrente."
  exit 0
fi

for notebook in "${notebooks[@]}"; do
  output_file="$OUTPUT_DIR/$notebook"

  if [[ -f "$output_file" ]]; then
    echo "Skip: $output_file esiste già."
    continue
  fi

  echo "Traduco: $notebook -> $output_file"

  python "$TRANSLATE_SCRIPT" \
    "$notebook" \
    --output "$output_file"
done

echo "Completato."
