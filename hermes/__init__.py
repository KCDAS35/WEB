"""
Hermes — PDF OCR Correction Agent Swarm

Processes PDFs riddled with OCR typos and produces clean .txt files.
Uses Claude Opus 4.6 with adaptive thinking for intelligent correction.
"""
from .pipeline import HermesPipeline
from .swarm import HermesSwarm

__all__ = ["HermesPipeline", "HermesSwarm"]
