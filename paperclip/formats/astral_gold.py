"""
Astral Gold (iOS) exporter.

Astral Gold uses an internal SQLite database and syncs via iCloud.
For bulk data import the most reliable method is exporting a CSV that
can be imported via the app's "Import Charts" feature, or via the
Astral Gold companion website.

Format: CSV with the following columns
  name, date (YYYY-MM-DD), time (HH:MM), latitude, longitude,
  timezone_offset, city, country, notes

Astral Gold for iOS also accepts Astrolog-format files (.as) for
compatibility with other Western astrology software.
"""
from __future__ import annotations

from pathlib import Path

from ..reader import BirthRecord


class AstralGoldExporter:
    """
    Export birth records for Astral Gold (iOS).

    Two formats:
    - CSV (primary — use File → Import in the app)
    - Astrolog (.as) format for compatibility

    Usage:
        exp = AstralGoldExporter()
        exp.export(records, "charts_astral_gold.csv")
    """

    HEADER = "name,date,time,latitude,longitude,timezone_offset,city,country,notes"

    def export(self, records: list[BirthRecord], output_path: str | Path) -> Path:
        """Export to Astral Gold CSV import format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [self.HEADER]
        for r in records:
            date = f"{r.year:04d}-{r.month:02d}-{r.day:02d}"
            time = f"{r.hour:02d}:{r.minute:02d}"
            tz = f"{r.timezone_offset:+.2f}"

            def q(s: str) -> str:
                if "," in s or '"' in s:
                    return '"' + s.replace('"', '""') + '"'
                return s

            lines.append(
                f"{q(r.name)},{date},{time},{r.latitude:.6f},{r.longitude:.6f},"
                f"{tz},{q(r.city)},{q(r.country)},{q(r.notes)}"
            )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def export_astrolog(self, records: list[BirthRecord], output_dir: str | Path) -> list[Path]:
        """
        Export each record as an Astrolog .as file.
        Astrolog format is understood by many Western astrology apps.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []

        for r in records:
            safe_name = "".join(c for c in r.name if c.isalnum() or c in " _-").strip()
            safe_name = safe_name.replace(" ", "_") or f"chart_{id(r)}"
            out_path = out_dir / f"{safe_name}.as"

            # Astrolog command-line format
            lon_sign = 1 if r.longitude >= 0 else -1
            lat_sign = 1 if r.latitude >= 0 else -1
            lon_deg = abs(r.longitude)
            lat_deg = abs(r.latitude)

            content = (
                f"-zi \"{r.name}\"\n"
                f"-zd {r.month}/{r.day}/{r.year}\n"
                f"-zt {r.hour}:{r.minute:02d}:{r.second:02d}\n"
                f"-zz {r.timezone_offset:+.1f}\n"
                f"-zl {lon_deg:.4f}{'E' if r.longitude >= 0 else 'W'} "
                f"{lat_deg:.4f}{'N' if r.latitude >= 0 else 'S'}\n"
                f"-zn \"{r.city}, {r.country}\"\n"
            )

            out_path.write_text(content, encoding="utf-8")
            paths.append(out_path)

        return paths
