
import re
import sys
import unicodedata
from pathlib import Path
INPUT_PATH = Path(r"C:OneDrive\Desktop\ORIGINAL\raw_corpus.txt")
CLEANED_NAME = "cleaned_corpus.txt"
TOKENS_NAME = "tokenized_words.txt"
# A word = letters, optionally joined by ' or - (e.g. ng'ombe, kila-siku)
WORD_RE = re.compile(r"[^\W\d_]+(?:['\-][^\W\d_]+)*")
URL_RE = re.compile(r"(https?://\S+|www\.\S+)", re.IGNORECASE)
EMAIL_RE = re.compile(r"\S+@\S+\.\S+")
HTML_RE = re.compile(r"<[^>]+>")
SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
def find_input() -> Path:
    """Use the command-line path if given, otherwise INPUT_PATH, then fallbacks."""
    candidates = []
    if len(sys.argv) > 1:
        candidates.append(Path(sys.argv[1]))
    candidates += [
        INPUT_PATH,
        Path.home() / "OneDrive" / "Desktop" / "ORIGINAL" / "raw_corpus.txt",
        Path.home() / "Desktop" / "ORIGINAL" / "raw_corpus.txt",
        Path(__file__).resolve().parent / "raw_corpus.txt",
        Path.cwd() / "raw_corpus.txt",
    ]
    for path in candidates:
        if path.exists():
            return path
    print("Could not find raw_corpus.txt. I looked in:")
    for path in candidates:
        print(f"  {path}")
    sys.exit(
        "\nFix: edit INPUT_PATH at the top of this script, or run:\n"
        '    python preprocess.py "full\\path\\to\\raw_corpus.txt"'
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
        tokens = WORD_RE.findall(sentence)
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
