"""
AstroConverter — converts birth data to all supported software formats.
"""
from __future__ import annotations

from pathlib import Path

from .reader import BirthDataReader, BirthRecord
from .formats import (
    SolarFireExporter,
    AstralGoldExporter,
    ParasharaExporter,
    JyotishExporter,
)

ALL_FORMATS = ("solar_fire", "astral_gold", "parashara", "jyotish")


class AstroConverter:
    """
    Read an Excel/CSV file and convert to one or more software formats.

    Usage:
        converter = AstroConverter()
        outputs = converter.convert_all("birth_data.xlsx", output_dir="./exports")
    """

    def __init__(self) -> None:
        self.reader = BirthDataReader()
        self._exporters = {
            "solar_fire": SolarFireExporter(),
            "astral_gold": AstralGoldExporter(),
            "parashara": ParasharaExporter(),
            "jyotish": JyotishExporter(),
        }

    def read(self, input_path: str | Path) -> list[BirthRecord]:
        """Read birth data from Excel or CSV."""
        return self.reader.read(input_path)

    def convert(
        self,
        input_path: str | Path,
        formats: list[str] | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, list[Path]]:
        """
        Convert input file to specified software formats.

        Args:
            input_path: Path to Excel or CSV file
            formats: List of formats to export. If None, exports all.
                     Options: "solar_fire", "astral_gold", "parashara", "jyotish"
            output_dir: Directory for output files. Defaults to same dir as input.

        Returns:
            Dict mapping format name → list of output paths
        """
        input_path = Path(input_path)
        formats = formats or list(ALL_FORMATS)
        out_dir = Path(output_dir) if output_dir else input_path.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        records = self.read(input_path)
        if not records:
            raise ValueError(f"No valid birth records found in {input_path}")

        stem = input_path.stem
        results: dict[str, list[Path]] = {}

        if "solar_fire" in formats:
            exp = self._exporters["solar_fire"]
            path = exp.export(records, out_dir / f"{stem}_solar_fire.txt")
            results["solar_fire"] = [path]

        if "astral_gold" in formats:
            exp = self._exporters["astral_gold"]
            path = exp.export(records, out_dir / f"{stem}_astral_gold.csv")
            results["astral_gold"] = [path]

        if "parashara" in formats:
            exp = self._exporters["parashara"]
            path_tab = exp.export(records, out_dir / f"{stem}_parashara.txt")
            path_csv = exp.export_kundali_format(records, out_dir / f"{stem}_kundali.csv")
            results["parashara"] = [path_tab, path_csv]

        if "jyotish" in formats:
            exp = self._exporters["jyotish"]
            path_csv = exp.export(records, out_dir / f"{stem}_jyotish9.csv")
            path_json = exp.export_native(records, out_dir / f"{stem}_jyotish9.json")
            results["jyotish"] = [path_csv, path_json]

        return results

    def convert_all(
        self,
        input_path: str | Path,
        output_dir: str | Path | None = None,
    ) -> dict[str, list[Path]]:
        """Convert to all supported formats."""
        return self.convert(input_path, formats=list(ALL_FORMATS), output_dir=output_dir)

    def preview(self, input_path: str | Path, n: int = 5) -> list[BirthRecord]:
        """Return the first n records for inspection."""
        return self.read(input_path)[:n]
