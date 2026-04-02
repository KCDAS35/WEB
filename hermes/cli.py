"""
Hermes CLI — correct OCR errors in PDF files.

Usage:
    python -m hermes correct scan.pdf
    python -m hermes correct *.pdf --output ./clean/ --swarm
"""
import sys
from pathlib import Path

import click

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn
    console = Console()
except ImportError:
    console = None


@click.group()
def cli():
    """Hermes — PDF OCR correction agent swarm."""
    pass


@cli.command()
@click.argument("pdfs", nargs=-1, required=True, type=click.Path(exists=True))
@click.option("--output", "-o", default=None, help="Output directory for .txt files")
@click.option("--swarm", is_flag=True, help="Use parallel agent swarm (requires claude-agent-sdk)")
@click.option("--verbose", "-v", is_flag=True, help="Show correction progress")
def correct(pdfs: tuple[str, ...], output: str | None, swarm: bool, verbose: bool) -> None:
    """Correct OCR errors in one or more PDF files."""
    pdf_paths = [Path(p) for p in pdfs]

    if swarm:
        from .swarm import HermesSwarm
        processor = HermesSwarm(output_dir=output, verbose=verbose)
    else:
        from .pipeline import HermesPipeline
        processor = HermesPipeline(output_dir=output, verbose=verbose)

    for pdf_path in pdf_paths:
        click.echo(f"Processing: {pdf_path.name}")
        try:
            out = processor.correct(pdf_path)
            click.echo(f"  → {out}")
        except Exception as e:
            click.echo(f"  ERROR: {e}", err=True)
            sys.exit(1)


if __name__ == "__main__":
    cli()
