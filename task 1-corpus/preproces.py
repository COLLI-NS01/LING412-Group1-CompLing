"""
Clean and tokenise a Kiswahili corpus.

Input : raw_corpus.txt
Output: cleaned_corpus.txt   (one cleaned sentence per line)
        tokenized_words.txt  (one word/token per line)

Usage:
    python preprocess.py                      # looks for raw_corpus.txt next to this script
    python preprocess.py "C:\\path\\to\\raw_corpus.txt"
"""

import re
import sys
import unicodedata
from pathlib import Path

INPUT_NAME = "raw_corpus.txt"
CLEANED_NAME = "cleaned_corpus.txt"
TOKENS_NAME = "tokenized_words.txt"

# A word = letters, optionally joined by ' or - (e.g. ng'ombe, kila-siku)
WORD_RE = re.compile(r"[^\W\d_]+(?:['\-][^\W\d_]+)*")
URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
HTML_RE = re.compile(r"<[^>]+>")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def find_input() -> Path:
    """Find raw_corpus.txt: command-line path, script folder, then current folder."""
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        if path.exists():
            return path
        sys.exit(f"File not found: {path}")

    script_dir = Path(__file__).resolve().parent
    for folder in (script_dir, Path.cwd()):
        path = folder / INPUT_NAME
        if path.exists():
            return path

    sys.exit(
        f"Could not find '{INPUT_NAME}'.\n"
        f"Looked in: {script_dir} and {Path.cwd()}\n"
        f"Put the file next to this script, or run:\n"
        f'    python preprocess.py "full\\path\\to\\{INPUT_NAME}"'
    )


def read_text(path: Path) -> str:
    """Read the file, trying common encodings."""
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    sys.exit("Could not decode the file. Please save it as UTF-8.")


def normalise(text: str) -> str:
    """Unicode-normalise, standardise quotes, lowercase, strip URLs/emails/HTML."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace("\u2019", "'").replace("\u2018", "'").replace("`", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.lower()
    text = URL_RE.sub(" ", text)
    text = EMAIL_RE.sub(" ", text)
    text = HTML_RE.sub(" ", text)
    return text


def split_sentences(text: str) -> list[str]:
    """Split on line breaks first, then on . ! ? boundaries."""
    sentences = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        sentences.extend(s.strip() for s in SENT_SPLIT_RE.split(line) if s.strip())
    return sentences


def main() -> None:
    input_path = find_input()
    out_dir = input_path.parent

    raw = read_text(input_path)
    text = normalise(raw)
    sentences = split_sentences(text)

    cleaned_sentences = []
    all_tokens = []

    for sentence in sentences:
        tokens = WORD_RE.findall(sentence)  # drops digits, punctuation, symbols
        if not tokens:
            continue
        cleaned_sentences.append(" ".join(tokens))
        all_tokens.extend(tokens)

    (out_dir / CLEANED_NAME).write_text("\n".join(cleaned_sentences), encoding="utf-8")
    (out_dir / TOKENS_NAME).write_text("\n".join(all_tokens), encoding="utf-8")

    print(f"Input            : {input_path}")
    print(f"Sentences kept   : {len(cleaned_sentences)}")
    print(f"Total tokens     : {len(all_tokens)}")
    print(f"Unique tokens    : {len(set(all_tokens))}")
    print(f"Saved cleaned    : {out_dir / CLEANED_NAME}")
    print(f"Saved tokens     : {out_dir / TOKENS_NAME}")


if __name__ == "__main__":
    main()
