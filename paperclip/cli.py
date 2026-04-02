"""
Paperclip CLI — convert astrological birth data files.

Usage:
    python -m paperclip convert charts.xlsx
    python -m paperclip convert charts.xlsx --format solar_fire --output ./exports/
    python -m paperclip preview charts.xlsx
"""
import sys
from pathlib import Path

import click


@click.group()
def cli():
    """Paperclip — astrological data file converter."""
    pass


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option(
    "--format", "-f", "formats",
    multiple=True,
    type=click.Choice(["solar_fire", "astral_gold", "parashara", "jyotish", "all"]),
    default=["all"],
    help="Target software format(s). Default: all",
)
@click.option("--output", "-o", default=None, help="Output directory")
def convert(input_file: str, formats: tuple[str, ...], output: str | None) -> None:
    """Convert birth data file to astrological software formats."""
    from .converter import AstroConverter

    converter = AstroConverter()
    selected = list(formats)
    if "all" in selected:
        selected = None  # None = all formats

    try:
        results = converter.convert(input_file, formats=selected, output_dir=output)
        for fmt, paths in results.items():
            for path in paths:
                click.echo(f"[{fmt}] → {path}")
    except Exception as e:
        click.echo(f"ERROR: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--rows", "-n", default=5, help="Number of records to show")
def preview(input_file: str, rows: int) -> None:
    """Preview birth records from a file."""
    from .converter import AstroConverter

    converter = AstroConverter()
    records = converter.preview(input_file, n=rows)

    if not records:
        click.echo("No records found.")
        return

    click.echo(f"\nFound {rows} record(s) (showing first {min(rows, len(records))}):\n")
    for r in records:
        click.echo(f"  Name:     {r.name}")
        click.echo(f"  Date:     {r.date_str}")
        click.echo(f"  Time:     {r.time_str}")
        click.echo(f"  Place:    {r.city}, {r.country}")
        click.echo(f"  Lat/Lon:  {r.lat_str} / {r.lon_str}")
        click.echo(f"  Timezone: {r.timezone_name} (UTC{r.timezone_offset:+.2f})")
        if r.notes:
            click.echo(f"  Notes:    {r.notes}")
        click.echo()


if __name__ == "__main__":
    cli()
