"""
Hermes Pipeline — single-file OCR correction using Claude API directly.

For each PDF:
  1. Extract raw text (pdfplumber)
  2. Split into chunks
  3. Correct each chunk with Claude (streaming, adaptive thinking)
  4. Reassemble and save as .txt
"""
from __future__ import annotations

import os
import re
import textwrap
from pathlib import Path
from typing import Iterator

import anthropic

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


CHUNK_SIZE = 2000  # characters per chunk — keeps each API call manageable

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert OCR post-processor. You receive raw text extracted from a
    scanned document that is riddled with OCR errors — misread characters,
    broken words, spurious hyphens, merged words, garbled punctuation, and
    similar artifacts.

    Your job is to return the CORRECTED text. Rules:
    - Fix OCR errors (e.g. "tbe" → "the", "rn" → "m", "l" → "I" where context demands)
    - Rejoin words split by line-break hyphens (e.g. "inter-\nesting" → "interesting")
    - Remove running headers/footers/page numbers that interrupt the main text
    - Preserve paragraph structure
    - Do NOT add content that was not in the original
    - Do NOT remove content that appears intentional
    - Return ONLY the corrected text — no commentary, no markdown, no preamble
""")


def _extract_text_pdfplumber(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        pages = []
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text)
        return "\n\n".join(pages)


def _extract_text_pypdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages)


def extract_text(path: Path) -> str:
    """Extract raw text from a PDF using the best available library."""
    if HAS_PDFPLUMBER:
        return _extract_text_pdfplumber(path)
    elif HAS_PYPDF:
        return _extract_text_pypdf(path)
    else:
        raise RuntimeError(
            "No PDF library found. Install pdfplumber: pip install pdfplumber"
        )


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """Split text into chunks at paragraph boundaries when possible."""
    if len(text) <= size:
        return [text]

    chunks: list[str] = []
    paragraphs = re.split(r"\n{2,}", text)
    current = ""

    for para in paragraphs:
        if len(current) + len(para) + 2 <= size:
            current = (current + "\n\n" + para).lstrip()
        else:
            if current:
                chunks.append(current)
            # If a single paragraph exceeds size, hard-split it
            if len(para) > size:
                for i in range(0, len(para), size):
                    chunks.append(para[i : i + size])
                current = ""
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def correct_chunk(client: anthropic.Anthropic, chunk: str, verbose: bool = False) -> str:
    """Send one chunk to Claude for OCR correction (streaming)."""
    corrected_parts: list[str] = []

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Correct this OCR text:\n\n{chunk}"}],
    ) as stream:
        for event in stream:
            if (
                event.type == "content_block_delta"
                and event.delta.type == "text_delta"
            ):
                corrected_parts.append(event.delta.text)
                if verbose:
                    print(event.delta.text, end="", flush=True)

    return "".join(corrected_parts)


class HermesPipeline:
    """
    Corrects a single PDF file and writes a clean .txt output.

    Usage:
        pipeline = HermesPipeline()
        output_path = pipeline.correct("scan.pdf")
    """

    def __init__(
        self,
        api_key: str | None = None,
        output_dir: str | Path | None = None,
        verbose: bool = False,
    ) -> None:
        self.client = anthropic.Anthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY")
        )
        self.output_dir = Path(output_dir) if output_dir else None
        self.verbose = verbose

    def correct(self, pdf_path: str | Path) -> Path:
        """
        Correct OCR errors in a PDF and return the path to the clean .txt file.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        # Determine output path
        out_dir = self.output_dir or pdf_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (pdf_path.stem + "_corrected.txt")

        if self.verbose:
            print(f"[Hermes] Extracting text from {pdf_path.name}...")

        raw_text = extract_text(pdf_path)

        if not raw_text.strip():
            raise ValueError(f"No text extracted from {pdf_path}. Is it a scanned image-only PDF?")

        chunks = chunk_text(raw_text)

        if self.verbose:
            print(f"[Hermes] Processing {len(chunks)} chunk(s) with Claude Opus 4.6...")

        corrected_chunks: list[str] = []
        for i, chunk in enumerate(chunks, 1):
            if self.verbose:
                print(f"\n[Hermes] Chunk {i}/{len(chunks)}:")
            corrected = correct_chunk(self.client, chunk, verbose=self.verbose)
            corrected_chunks.append(corrected)

        final_text = "\n\n".join(corrected_chunks)

        out_path.write_text(final_text, encoding="utf-8")

        if self.verbose:
            print(f"\n[Hermes] Saved to {out_path}")

        return out_path

    def correct_many(self, pdf_paths: list[str | Path]) -> list[Path]:
        """Correct multiple PDFs sequentially."""
        return [self.correct(p) for p in pdf_paths]
