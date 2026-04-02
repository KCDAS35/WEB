"""
Solar Fire Gold exporter.

Solar Fire can import chart data from a tab-delimited text file (.txt) using
File → Import Chart Data. The expected format is:

  Name [TAB] Date [TAB] Time [TAB] City [TAB] Country [TAB] Lat [TAB] Lon [TAB] TZ

  Date: DD/MM/YYYY
  Time: HH:MM:SS
  Lat:  DD°MM'N/S   (e.g. 51°30'N)
  Lon:  DDD°MM'E/W  (e.g. 000°07'W)
  TZ:   ±HH:MM      (e.g. +00:00)

Reference: Solar Fire Gold User Guide, Chapter 3, "Importing Charts"
"""
from __future__ import annotations

from pathlib import Path

from ..reader import BirthRecord


def _tz_str(offset_hours: float) -> str:
    """Convert decimal hours to ±HH:MM format."""
    sign = "+" if offset_hours >= 0 else "-"
    abs_h = abs(offset_hours)
    h = int(abs_h)
    m = int(round((abs_h - h) * 60))
    return f"{sign}{h:02d}:{m:02d}"


def _lat_sf(lat: float) -> str:
    """Solar Fire latitude format: DD°MM'N or DD°MM'S."""
    ns = "N" if lat >= 0 else "S"
    deg = abs(lat)
    d = int(deg)
    m = int(round((deg - d) * 60))
    return f"{d:02d}°{m:02d}'{ns}"


def _lon_sf(lon: float) -> str:
    """Solar Fire longitude format: DDD°MM'E or DDD°MM'W."""
    ew = "E" if lon >= 0 else "W"
    deg = abs(lon)
    d = int(deg)
    m = int(round((deg - d) * 60))
    return f"{d:03d}°{m:02d}'{ew}"


class SolarFireExporter:
    """
    Export birth records to Solar Fire import format.

    Usage:
        exp = SolarFireExporter()
        exp.export(records, "charts_solar_fire.txt")
    """

    HEADER = "Name\tDate\tTime\tCity\tCountry\tLatitude\tLongitude\tTimezone"

    def export(self, records: list[BirthRecord], output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [self.HEADER]
        for r in records:
            date = f"{r.day:02d}/{r.month:02d}/{r.year:04d}"
            time = f"{r.hour:02d}:{r.minute:02d}:{r.second:02d}"
            lat = _lat_sf(r.latitude)
            lon = _lon_sf(r.longitude)
            tz = _tz_str(r.timezone_offset)
            lines.append(
                f"{r.name}\t{date}\t{time}\t{r.city}\t{r.country}\t{lat}\t{lon}\t{tz}"
            )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def export_csv(self, records: list[BirthRecord], output_path: str | Path) -> Path:
        """Alternative CSV format for Solar Fire import."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = ["Name,Date,Time,City,Country,Latitude,Longitude,Timezone"]
        for r in records:
            date = f"{r.day:02d}/{r.month:02d}/{r.year:04d}"
            time = f"{r.hour:02d}:{r.minute:02d}:{r.second:02d}"
            lat = _lat_sf(r.latitude)
            lon = _lon_sf(r.longitude)
            tz = _tz_str(r.timezone_offset)
            # Quote fields that may contain commas
            name = f'"{r.name}"' if "," in r.name else r.name
            city = f'"{r.city}"' if "," in r.city else r.city
            lines.append(f"{name},{date},{time},{city},{r.country},{lat},{lon},{tz}")

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path
