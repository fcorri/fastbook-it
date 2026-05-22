#!/usr/bin/env python3

import argparse
import json
import time
from pathlib import Path
from deep_translator import GoogleTranslator


def split_text(text, max_chars=4500):
    """
    Divide il testo in blocchi per evitare limiti di lunghezza della traduzione.
    Cerca di spezzare su paragrafi o righe quando possibile.
    """
    if len(text) <= max_chars:
        return [text]

    chunks = []
    current = ""

    for line in text.splitlines(keepends=True):
        if len(current) + len(line) > max_chars:
            if current:
                chunks.append(current)
                current = ""
        current += line

    if current:
        chunks.append(current)

    return chunks


def translate_text(text, source_lang, target_lang, delay=0.3):
    """
    Traduce un testo preservando blocchi vuoti.
    """
    if not text.strip():
        return text

    translator = GoogleTranslator(source=source_lang, target=target_lang)
    chunks = split_text(text)

    translated_chunks = []

    for chunk in chunks:
        translated = translator.translate(chunk)
        translated_chunks.append(translated)
        time.sleep(delay)

    return "".join(translated_chunks)


def translate_notebook(input_path, output_path, source_lang, target_lang, cell_types):
    input_path = Path(input_path)
    output_path = Path(output_path)

    with input_path.open("r", encoding="utf-8") as f:
        notebook = json.load(f)

    translated_count = 0

    for cell in notebook.get("cells", []):
        cell_type = cell.get("cell_type")

        if cell_type not in cell_types:
            continue

        source = cell.get("source", [])

        if isinstance(source, list):
            original_text = "".join(source)
        else:
            original_text = source

        if not original_text.strip():
            continue

        translated_text = translate_text(
            original_text,
            source_lang=source_lang,
            target_lang=target_lang,
        )

        # I notebook di solito salvano source come lista di righe.
        cell["source"] = translated_text.splitlines(keepends=True)

        translated_count += 1
        print(f"Tradotta cella {translated_count}: tipo={cell_type}")

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False, indent=1)

    print()
    print(f"Completato. Celle tradotte: {translated_count}")
    print(f"File salvato in: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Traduce le celle testuali di un Jupyter Notebook usando Google Translate."
    )

    parser.add_argument(
        "input",
        help="Percorso del notebook originale .ipynb",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Percorso del notebook tradotto. Default: <nome>_translated.ipynb",
    )

    parser.add_argument(
        "--source",
        default="en",
        help="Lingua sorgente. Default: en",
    )

    parser.add_argument(
        "--target",
        default="it",
        help="Lingua di destinazione. Default: it",
    )

    parser.add_argument(
        "--cell-types",
        nargs="+",
        default=["markdown", "raw"],
        choices=["markdown", "raw", "code"],
        help="Tipi di celle da tradurre. Default: markdown raw",
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = input_path.with_name(input_path.stem + "_translated.ipynb")

    translate_notebook(
        input_path=input_path,
        output_path=output_path,
        source_lang=args.source,
        target_lang=args.target,
        cell_types=set(args.cell_types),
    )


if __name__ == "__main__":
    main()
