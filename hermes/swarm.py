"""
Hermes Swarm — parallel OCR correction using Claude Agent SDK subagents.

Each chunk is processed by a dedicated subagent running concurrently,
dramatically speeding up large documents.

Requires: pip install claude-agent-sdk
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path

from .pipeline import extract_text, chunk_text, CHUNK_SIZE

try:
    from claude_agent_sdk import query, ClaudeAgentOptions, AgentDefinition, ResultMessage
    HAS_AGENT_SDK = True
except ImportError:
    HAS_AGENT_SDK = False


CORRECTOR_SYSTEM_PROMPT = """\
You are an expert OCR post-processor. You receive raw text extracted from a
scanned document riddled with OCR errors.

Fix all OCR errors: misread characters (e.g. "tbe"→"the", "rn"→"m"),
broken hyphenated words, merged words, page headers/footers interrupting text.
Preserve paragraph structure. Return ONLY the corrected text — no commentary.
"""


async def _correct_chunk_agent(chunk: str, chunk_id: int) -> tuple[int, str]:
    """Run one chunk through a Claude agent and return (chunk_id, corrected_text)."""
    result_text = ""
    async for message in query(
        prompt=f"Correct the OCR errors in this text chunk:\n\n{chunk}",
        options=ClaudeAgentOptions(
            system_prompt=CORRECTOR_SYSTEM_PROMPT,
        ),
    ):
        if isinstance(message, ResultMessage):
            result_text = message.result
            break

    return chunk_id, result_text


class HermesSwarm:
    """
    Parallel OCR correction using Claude Agent SDK.

    Spawns one agent per chunk and runs them concurrently.
    Falls back to HermesPipeline if agent SDK is not installed.

    Usage:
        swarm = HermesSwarm()
        output_path = swarm.correct("scan.pdf")
    """

    def __init__(
        self,
        output_dir: str | Path | None = None,
        verbose: bool = False,
        max_concurrent: int = 5,
    ) -> None:
        if not HAS_AGENT_SDK:
            raise ImportError(
                "claude-agent-sdk is required for HermesSwarm.\n"
                "Install it with: pip install claude-agent-sdk\n"
                "Or use HermesPipeline for sequential processing."
            )
        self.output_dir = Path(output_dir) if output_dir else None
        self.verbose = verbose
        self.max_concurrent = max_concurrent

    def correct(self, pdf_path: str | Path) -> Path:
        """Synchronous wrapper around the async swarm."""
        return asyncio.run(self._correct_async(pdf_path))

    async def _correct_async(self, pdf_path: str | Path) -> Path:
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        out_dir = self.output_dir or pdf_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / (pdf_path.stem + "_corrected.txt")

        if self.verbose:
            print(f"[HermesSwarm] Extracting text from {pdf_path.name}...")

        raw_text = extract_text(pdf_path)

        if not raw_text.strip():
            raise ValueError(f"No text extracted from {pdf_path}.")

        chunks = chunk_text(raw_text)

        if self.verbose:
            print(f"[HermesSwarm] Launching {len(chunks)} agent(s) in parallel (max {self.max_concurrent} concurrent)...")

        # Process in batches to respect max_concurrent
        results: dict[int, str] = {}
        semaphore = asyncio.Semaphore(self.max_concurrent)

        async def bounded_correct(idx: int, chunk: str) -> None:
            async with semaphore:
                if self.verbose:
                    print(f"[HermesSwarm] Agent {idx + 1}/{len(chunks)} started...")
                chunk_id, corrected = await _correct_chunk_agent(chunk, idx)
                results[chunk_id] = corrected
                if self.verbose:
                    print(f"[HermesSwarm] Agent {idx + 1}/{len(chunks)} done.")

        await asyncio.gather(*[bounded_correct(i, c) for i, c in enumerate(chunks)])

        # Reassemble in order
        ordered = [results[i] for i in range(len(chunks))]
        final_text = "\n\n".join(ordered)

        out_path.write_text(final_text, encoding="utf-8")

        if self.verbose:
            print(f"[HermesSwarm] Saved to {out_path}")

        return out_path

    def correct_many(self, pdf_paths: list[str | Path]) -> list[Path]:
        return [self.correct(p) for p in pdf_paths]
