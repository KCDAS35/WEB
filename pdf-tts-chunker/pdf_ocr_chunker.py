#!/usr/bin/env python3
"""
PDF OCR Chunker — extracts text from PDFs (with OCR fallback for scanned pages),
cleans OCR artifacts (broken words, nonsense tokens, hyphenation), and outputs
text chunks at configurable character sizes suitable for TTS pipelines.
"""

import re
import os
import sys
import json
import logging
import unicodedata
from pathlib import Path
from typing import List, Tuple, Optional

import click
import fitz  # PyMuPDF
import nltk
from spellchecker import SpellChecker
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
# Words shorter than this are exempt from nonsense detection
MIN_WORD_LEN_FOR_CHECK = 4

# A word is "nonsense" if the ratio of non-alpha characters exceeds this
GARBAGE_RATIO_THRESHOLD = 0.5

# Tesseract page segmentation mode: assume a single uniform block of text
TESSERACT_CONFIG = "--psm 6 --oem 3"

# Minimum text characters on a page before we consider it "has text"
MIN_PAGE_TEXT_CHARS = 50


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_text_pymupdf(pdf_path: Path) -> List[Tuple[int, str]]:
    """
    Extract text page-by-page using PyMuPDF.
    Returns list of (page_number, raw_text).
    """
    pages = []
    doc = fitz.open(str(pdf_path))
    for i, page in enumerate(doc):
        text = page.get_text("text")
        pages.append((i + 1, text))
    doc.close()
    return pages


def ocr_page_image(image: Image.Image) -> str:
    """Run Tesseract OCR on a PIL image and return the text."""
    return pytesseract.image_to_string(image, config=TESSERACT_CONFIG)


def extract_text_with_ocr_fallback(
    pdf_path: Path,
    dpi: int = 300,
    force_ocr: bool = False,
) -> List[Tuple[int, str]]:
    """
    For each page:
      - If PyMuPDF returns enough text and force_ocr is False → use it directly.
      - Otherwise → render the page to an image and run Tesseract OCR.

    Returns list of (page_number, raw_text).
    """
    mupdf_pages = extract_text_pymupdf(pdf_path)
    result = []

    # Convert all pages to images once (lazy: only if any page needs OCR)
    images: Optional[List[Image.Image]] = None

    for page_num, mupdf_text in mupdf_pages:
        if not force_ocr and len(mupdf_text.strip()) >= MIN_PAGE_TEXT_CHARS:
            log.debug("Page %d: using PyMuPDF text (%d chars)", page_num, len(mupdf_text))
            result.append((page_num, mupdf_text))
        else:
            if images is None:
                log.info("OCR required — rendering %s to images at %d DPI…", pdf_path.name, dpi)
                images = convert_from_path(str(pdf_path), dpi=dpi)
            log.info("Page %d: running Tesseract OCR", page_num)
            ocr_text = ocr_page_image(images[page_num - 1])
            result.append((page_num, ocr_text))

    return result


# ---------------------------------------------------------------------------
# Text cleaning / post-processing
# ---------------------------------------------------------------------------

def normalize_unicode(text: str) -> str:
    """Normalize unicode, replace fancy quotes/dashes with ASCII equivalents."""
    text = unicodedata.normalize("NFKC", text)
    replacements = {
        "\u2018": "'", "\u2019": "'",   # curly single quotes
        "\u201c": '"', "\u201d": '"',   # curly double quotes
        "\u2013": "-", "\u2014": "-",   # en-dash, em-dash
        "\u2026": "...",                # ellipsis
        "\u00a0": " ",                  # non-breaking space
        "\u00ad": "",                   # soft hyphen
        "\ufb01": "fi", "\ufb02": "fl", # ligatures
        "\ufb03": "ffi", "\ufb04": "ffl",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text


def fix_hyphenated_line_breaks(text: str) -> str:
    """
    Rejoin words broken across lines with a hyphen, e.g.:
      'impor-\\ntant' → 'important'
    Also handles soft-hyphen variants.
    """
    # Pattern: word-char + hyphen + optional spaces + newline + optional spaces + word-char
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    return text


def remove_control_characters(text: str) -> str:
    """Strip non-printable / control characters except newlines and tabs."""
    return re.sub(r"[^\x09\x0A\x20-\x7E\x80-\xFF]", "", text)


def is_nonsense_word(word: str) -> bool:
    """
    Heuristic detector for OCR garbage tokens.
    A word is considered garbage if:
      - It's long enough to care about (>= MIN_WORD_LEN_FOR_CHECK)
      - AND it contains no vowels (aeiou)
      - OR its ratio of non-alpha chars is above GARBAGE_RATIO_THRESHOLD
      - OR it looks like a run of random consonants
    """
    if len(word) < MIN_WORD_LEN_FOR_CHECK:
        return False
    clean = re.sub(r"[^a-zA-Z]", "", word)
    if len(clean) == 0:
        return False  # purely numeric / punctuation — handled elsewhere

    # No vowels at all in a sufficiently long alphabetic token
    if len(clean) >= MIN_WORD_LEN_FOR_CHECK and not re.search(r"[aeiouAEIOU]", clean):
        return True

    # Too many non-alphabetic characters
    non_alpha = len(word) - len(clean)
    if non_alpha / len(word) > GARBAGE_RATIO_THRESHOLD:
        return True

    # Implausible consonant clusters (5+ consonants in a row with no vowel)
    if re.search(r"[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{6,}", word):
        return True

    return False


def flag_or_remove_nonsense(text: str, remove: bool = False) -> Tuple[str, List[str]]:
    """
    Scan for nonsense OCR tokens.
    If remove=True, delete them from the text.
    Returns (cleaned_text, list_of_flagged_tokens).
    """
    flagged = []
    tokens = re.split(r"(\s+)", text)
    result = []
    for token in tokens:
        word = re.sub(r"[^a-zA-Z]", "", token)
        if word and is_nonsense_word(word):
            flagged.append(token.strip())
            if not remove:
                result.append(f"[OCR?:{token.strip()}]")
            # else: skip entirely
        else:
            result.append(token)
    return "".join(result), flagged


def normalize_whitespace(text: str) -> str:
    """Collapse multiple spaces/tabs to one; preserve paragraph breaks."""
    # Preserve paragraph breaks (2+ newlines → double newline)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse inline whitespace
    text = re.sub(r"[ \t]+", " ", text)
    # Remove spaces at the beginning/end of lines
    text = re.sub(r"^ | $", "", text, flags=re.MULTILINE)
    return text.strip()


def clean_text(
    text: str,
    remove_nonsense: bool = False,
    fix_hyphens: bool = True,
) -> Tuple[str, List[str]]:
    """
    Full cleaning pipeline for raw OCR text.
    Returns (cleaned_text, list_of_flagged_nonsense_tokens).
    """
    text = normalize_unicode(text)
    text = remove_control_characters(text)
    if fix_hyphens:
        text = fix_hyphenated_line_breaks(text)
    text, flagged = flag_or_remove_nonsense(text, remove=remove_nonsense)
    text = normalize_whitespace(text)
    return text, flagged


# ---------------------------------------------------------------------------
# Sentence-aware chunking
# ---------------------------------------------------------------------------

def _ensure_nltk_tokenizer():
    try:
        nltk.data.find("tokenizers/punkt_tab")
    except LookupError:
        nltk.download("punkt_tab", quiet=True)


def sentence_tokenize(text: str) -> List[str]:
    """Split text into sentences using NLTK punkt tokenizer."""
    _ensure_nltk_tokenizer()
    return nltk.sent_tokenize(text)


def chunk_text(
    text: str,
    chunk_size: int,
    overlap: int = 0,
) -> List[str]:
    """
    Chunk text into pieces of at most `chunk_size` characters, breaking
    only at sentence boundaries.  If a single sentence exceeds chunk_size
    it is split at the nearest word boundary.

    `overlap` characters of the previous chunk are prepended to the next
    chunk (for context-aware TTS models).
    """
    sentences = sentence_tokenize(text)
    chunks: List[str] = []
    current: List[str] = []
    current_len = 0

    for sent in sentences:
        sent_len = len(sent)

        # Single sentence larger than chunk_size → hard-split at word boundary
        if sent_len > chunk_size:
            # Flush current buffer first
            if current:
                chunks.append(" ".join(current))
                current = []
                current_len = 0
            # Split long sentence at word boundaries
            words = sent.split()
            sub: List[str] = []
            sub_len = 0
            for word in words:
                if sub_len + len(word) + 1 > chunk_size and sub:
                    chunks.append(" ".join(sub))
                    sub = []
                    sub_len = 0
                sub.append(word)
                sub_len += len(word) + 1
            if sub:
                chunks.append(" ".join(sub))
            continue

        # Would adding this sentence exceed limit?
        addition = sent_len + (1 if current else 0)  # +1 for space separator
        if current and current_len + addition > chunk_size:
            chunks.append(" ".join(current))
            current = [sent]
            current_len = sent_len
        else:
            current.append(sent)
            current_len += addition

    if current:
        chunks.append(" ".join(current))

    # Apply overlap: prepend tail of previous chunk
    if overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            tail = chunks[i - 1][-overlap:]
            # Back-track to nearest word start
            space_idx = tail.find(" ")
            if space_idx != -1:
                tail = tail[space_idx + 1:]
            overlapped.append(tail + " " + chunks[i])
        return overlapped

    return chunks


# ---------------------------------------------------------------------------
# Report / output helpers
# ---------------------------------------------------------------------------

def write_chunks(
    chunks: List[str],
    output_dir: Path,
    stem: str,
    chunk_size: int,
) -> Path:
    """Write chunks as a JSON array and individual .txt files."""
    size_dir = output_dir / f"{stem}_chunks_{chunk_size}"
    size_dir.mkdir(parents=True, exist_ok=True)

    # JSON manifest
    manifest = {
        "source": stem,
        "chunk_size": chunk_size,
        "total_chunks": len(chunks),
        "chunks": [{"index": i, "chars": len(c), "text": c} for i, c in enumerate(chunks)],
    }
    json_path = size_dir / "manifest.json"
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    # Individual .txt files
    for i, chunk in enumerate(chunks):
        txt_path = size_dir / f"chunk_{i:04d}.txt"
        txt_path.write_text(chunk, encoding="utf-8")

    log.info(
        "  chunk_size=%d → %d chunks → %s",
        chunk_size,
        len(chunks),
        size_dir,
    )
    return size_dir


def write_cleaned_text(text: str, output_dir: Path, stem: str) -> Path:
    """Save the fully cleaned (pre-chunked) text for inspection."""
    path = output_dir / f"{stem}_cleaned.txt"
    path.write_text(text, encoding="utf-8")
    return path


def write_flag_report(flagged: List[str], output_dir: Path, stem: str) -> Optional[Path]:
    """Save a report of flagged OCR tokens."""
    if not flagged:
        return None
    path = output_dir / f"{stem}_ocr_flags.txt"
    unique = sorted(set(flagged))
    path.write_text(
        f"Flagged OCR tokens ({len(unique)} unique, {len(flagged)} total occurrences):\n\n"
        + "\n".join(unique),
        encoding="utf-8",
    )
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("pdf_files", nargs=-1, type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--input-dir", "-i",
    default=None,
    type=click.Path(exists=True, file_okay=False),
    help="Folder of PDFs to process (scanned recursively with --recursive).",
)
@click.option(
    "--recursive", "-R",
    is_flag=True,
    default=False,
    help="Search --input-dir recursively for PDFs.",
)
@click.option(
    "--output-dir", "-o",
    default="output",
    show_default=True,
    help="Directory to write output files.",
)
@click.option(
    "--chunk-sizes", "-c",
    default="500,1000,2000,4000",
    show_default=True,
    help="Comma-separated list of chunk sizes (in characters).",
)
@click.option(
    "--overlap", "-v",
    default=0,
    show_default=True,
    help="Overlap characters between consecutive chunks (0 = none).",
)
@click.option(
    "--force-ocr", "-f",
    is_flag=True,
    default=False,
    help="Force OCR on every page even if PyMuPDF finds text.",
)
@click.option(
    "--dpi", "-d",
    default=300,
    show_default=True,
    help="DPI for rendering PDF pages to images for OCR.",
)
@click.option(
    "--remove-nonsense", "-r",
    is_flag=True,
    default=False,
    help="Remove flagged OCR garbage tokens instead of tagging them [OCR?:…].",
)
@click.option(
    "--no-fix-hyphens",
    is_flag=True,
    default=False,
    help="Disable automatic rejoining of hyphenated line-break words.",
)
@click.option(
    "--verbose", "-V",
    is_flag=True,
    default=False,
    help="Enable debug logging.",
)
def main(
    pdf_files,
    input_dir,
    recursive,
    output_dir,
    chunk_sizes,
    overlap,
    force_ocr,
    dpi,
    remove_nonsense,
    no_fix_hyphens,
    verbose,
):
    """
    Extract, clean, and chunk text from PDF files for TTS pipelines.

    PDF_FILES  Zero or more individual PDF paths. Combine freely with --input-dir.

    Examples:

    \b
      # Process a whole folder of PDFs
      python pdf_ocr_chunker.py -i ./my_pdfs

    \b
      # Recursively scan a folder tree
      python pdf_ocr_chunker.py -i ./library -R

    \b
      # Mix a folder with extra individual files
      python pdf_ocr_chunker.py -i ./pdfs extra.pdf -o ./out

    \b
      # Force OCR, custom chunk sizes, remove garbage tokens
      python pdf_ocr_chunker.py --force-ocr --remove-nonsense -c 800,1600 doc.pdf

    \b
      # Multiple files, custom output dir, 100-char overlap
      python pdf_ocr_chunker.py -o ~/tts_chunks -v 100 file1.pdf file2.pdf
    """
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Collect PDFs from --input-dir
    dir_files: List[Path] = []
    if input_dir:
        base = Path(input_dir)
        pattern = "**/*.pdf" if recursive else "*.pdf"
        found = sorted(base.glob(pattern))
        # also catch uppercase .PDF
        found += sorted(base.glob(pattern.replace(".pdf", ".PDF")))
        dir_files = sorted(set(found))
        if not dir_files:
            click.echo(f"No PDF files found in: {input_dir}", err=True)
            sys.exit(1)
        log.info("Found %d PDF(s) in %s%s", len(dir_files), input_dir,
                 " (recursive)" if recursive else "")

    # Merge with individually-specified files (deduplicated, order preserved)
    seen = set()
    all_files: List[Path] = []
    for p in list(dir_files) + [Path(f) for f in pdf_files]:
        resolved = p.resolve()
        if resolved not in seen:
            seen.add(resolved)
            all_files.append(p)

    if not all_files:
        click.echo("No PDF files provided. Use -h for help.", err=True)
        sys.exit(1)

    log.info("Total PDFs to process: %d", len(all_files))

    try:
        sizes = [int(s.strip()) for s in chunk_sizes.split(",")]
    except ValueError:
        click.echo("--chunk-sizes must be comma-separated integers, e.g. 500,1000,2000", err=True)
        sys.exit(1)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for pdf_path in all_files:
        stem = pdf_path.stem
        log.info("=" * 60)
        log.info("Processing: %s", pdf_path)

        # --- Extract ---
        pages = extract_text_with_ocr_fallback(pdf_path, dpi=dpi, force_ocr=force_ocr)
        raw_text = "\n\n".join(page_text for _, page_text in pages)

        # --- Clean ---
        cleaned, flagged = clean_text(
            raw_text,
            remove_nonsense=remove_nonsense,
            fix_hyphens=not no_fix_hyphens,
        )

        cleaned_path = write_cleaned_text(cleaned, out_dir, stem)
        log.info("Cleaned text written → %s (%d chars)", cleaned_path, len(cleaned))

        if flagged:
            flag_path = write_flag_report(flagged, out_dir, stem)
            log.warning(
                "%d OCR garbage tokens flagged → %s",
                len(flagged),
                flag_path,
            )
        else:
            log.info("No OCR garbage tokens detected.")

        # --- Chunk ---
        log.info("Chunking at sizes: %s  (overlap=%d)", sizes, overlap)
        for size in sizes:
            chunks = chunk_text(cleaned, chunk_size=size, overlap=overlap)
            write_chunks(chunks, out_dir, stem, size)

        log.info("Done: %s", stem)

    log.info("=" * 60)
    log.info("All files processed. Output in: %s", out_dir.resolve())


if __name__ == "__main__":
    main()
