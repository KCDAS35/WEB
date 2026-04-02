"""
JyotisharSoftware 9 (also known as JyotishApp) exporter.

JyotisharSoftware 9 uses a CSV-based import format. The software
can import charts from:
  1. Its native .jyotish9 JSON-based format
  2. A standard CSV with specific column ordering
  3. Compatibility with Kala and Shri Jyoti Star formats

CSV column order for JyotisharSoftware 9 import:
  name, year, month, day, hour, minute, second,
  latitude, longitude, timezone, city, country, notes

The .jyotish9 format is JSON — each record is an object in a JSON array.
"""
from __future__ import annotations

import json
from pathlib import Path

from ..reader import BirthRecord


class JyotishExporter:
    """
    Export birth records for JyotisharSoftware 9.

    Two formats:
    - CSV (use File → Import Charts in the app)
    - Native JSON (.jyotish9) for direct chart loading

    Usage:
        exp = JyotishExporter()
        exp.export(records, "charts_jyotish9.csv")
        exp.export_native(records, "charts.jyotish9")
    """

    HEADER = (
        "name,year,month,day,hour,minute,second,"
        "latitude,longitude,timezone,city,country,notes"
    )

    def export(self, records: list[BirthRecord], output_path: str | Path) -> Path:
        """Export to JyotisharSoftware 9 CSV import format."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [self.HEADER]
        for r in records:
            def q(s: str) -> str:
                if "," in s or '"' in s:
                    return '"' + s.replace('"', '""') + '"'
                return s

            lines.append(
                f"{q(r.name)},{r.year},{r.month},{r.day},"
                f"{r.hour},{r.minute},{r.second},"
                f"{r.latitude:.6f},{r.longitude:.6f},"
                f"{r.timezone_offset:+.2f},"
                f"{q(r.city)},{q(r.country)},{q(r.notes)}"
            )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def export_native(self, records: list[BirthRecord], output_path: str | Path) -> Path:
        """
        Export to JyotisharSoftware 9 native JSON format (.jyotish9).
        This is a JSON array of chart objects.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        charts = []
        for r in records:
            charts.append({
                "name": r.name,
                "birth_date": {
                    "year": r.year,
                    "month": r.month,
                    "day": r.day,
                },
                "birth_time": {
                    "hour": r.hour,
                    "minute": r.minute,
                    "second": r.second,
                },
                "location": {
                    "city": r.city,
                    "country": r.country,
                    "latitude": r.latitude,
                    "longitude": r.longitude,
                    "timezone_offset": r.timezone_offset,
                    "timezone_name": r.timezone_name,
                },
                "notes": r.notes,
                "software": "JyotisharSoftware9",
                "format_version": "1.0",
            })

        output_path.write_text(
            json.dumps(charts, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )
        return output_path

    def export_kala_compat(self, records: list[BirthRecord], output_path: str | Path) -> Path:
        """
        Export in Kala software CSV format — compatible with JyotisharSoftware 9
        when using the Kala import option.

        Kala format: Name,Date(MM/DD/YYYY),Time(HH:MM:SS),Lat,Lon,TZ,Place
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = ["Name,Date,Time,Latitude,Longitude,Timezone,Place"]
        for r in records:
            date = f"{r.month:02d}/{r.day:02d}/{r.year:04d}"
            time = f"{r.hour:02d}:{r.minute:02d}:{r.second:02d}"
            place = f"{r.city}, {r.country}".strip(", ")

            def q(s: str) -> str:
                return f'"{s}"' if "," in s else s

            lines.append(
                f"{q(r.name)},{date},{time},"
                f"{r.latitude:.6f},{r.longitude:.6f},"
                f"{r.timezone_offset:+.2f},{q(place)}"
            )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path
