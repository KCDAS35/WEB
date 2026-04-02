#!/usr/bin/env python3
"""
main.py — unified entry point for Hermes and Paperclip.

Usage:
    python main.py hermes correct scan.pdf
    python main.py hermes correct *.pdf --output ./clean/ --swarm
    python main.py paperclip convert charts.xlsx
    python main.py paperclip preview charts.xlsx
    python main.py paperclip convert charts.xlsx --format solar_fire --output ./exports/

Environment:
    ANTHROPIC_API_KEY — required for Hermes OCR correction
"""
import sys
import click

from hermes.cli import cli as hermes_cli
from paperclip.cli import cli as paperclip_cli


@click.group()
def main():
    """
    Hermes + Paperclip — PDF OCR correction and astrological data pipeline.

    \b
    HERMES:    Correct OCR errors in scanned PDFs using Claude AI
    PAPERCLIP: Convert birth data to Solar Fire, Astral Gold, Parashara, Jyotish
    """
    pass


main.add_command(hermes_cli, name="hermes")
main.add_command(paperclip_cli, name="paperclip")


if __name__ == "__main__":
    main()
