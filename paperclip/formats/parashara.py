"""
Parashara's Light 9 exporter.

Parashara's Light 9 (by GeoVision Software) stores charts in its own
proprietary binary database. However it supports import via:

1. A tab-delimited text file via File → Import Charts
2. The "Kundali Data" exchange format used across Jyotish software

The tab-delimited format expected by Parashara's Light:
  Name [TAB] Day [TAB] Month [TAB] Year [TAB] Hour [TAB] Min [TAB] Sec
  [TAB] Lat_Deg [TAB] Lat_Min [TAB] N/S [TAB] Lon_Deg [TAB] Lon_Min
  [TAB] E/W [TAB] TZ_Hours [TAB] TZ_Mins [TAB] City [TAB] Country

Note: Parashara's Light uses LOCAL time (not UTC), and the timezone
field corrects to UTC internally.
"""
from __future__ import annotations

from pathlib import Path

from ..reader import BirthRecord


def _dms(degrees: float) -> tuple[int, int, int]:
    """Convert decimal degrees to (degrees, minutes, seconds)."""
    d = int(abs(degrees))
    rem = (abs(degrees) - d) * 60
    m = int(rem)
    s = int((rem - m) * 60)
    return d, m, s


class ParasharaExporter:
    """
    Export birth records for Parashara's Light 9.

    Usage:
        exp = ParasharaExporter()
        exp.export(records, "charts_parashara.txt")
    """

    HEADER = (
        "Name\tDay\tMonth\tYear\tHour\tMin\tSec\t"
        "Lat_Deg\tLat_Min\tNS\tLon_Deg\tLon_Min\tEW\t"
        "TZ_Hours\tTZ_Mins\tCity\tCountry"
    )

    def export(self, records: list[BirthRecord], output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [self.HEADER]
        for r in records:
            lat_d, lat_m, _ = _dms(r.latitude)
            lon_d, lon_m, _ = _dms(r.longitude)
            ns = "N" if r.latitude >= 0 else "S"
            ew = "E" if r.longitude >= 0 else "W"

            # Timezone: split into hours and minutes
            tz_h = int(abs(r.timezone_offset))
            tz_m = int(round((abs(r.timezone_offset) - tz_h) * 60))
            tz_sign = "+" if r.timezone_offset >= 0 else "-"
            # Parashara's Light typically expects the sign embedded in hours
            tz_hours_signed = tz_h if r.timezone_offset >= 0 else -tz_h

            lines.append(
                f"{r.name}\t{r.day}\t{r.month}\t{r.year}\t"
                f"{r.hour}\t{r.minute}\t{r.second}\t"
                f"{lat_d}\t{lat_m}\t{ns}\t"
                f"{lon_d}\t{lon_m}\t{ew}\t"
                f"{tz_hours_signed}\t{tz_m}\t"
                f"{r.city}\t{r.country}"
            )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def export_kundali_format(self, records: list[BirthRecord], output_path: str | Path) -> Path:
        """
        Export in the Kundali exchange format — a simple CSV accepted by
        multiple Jyotish applications including Parashara's Light.

        Format:
          Name,DD,MM,YYYY,HH,MM,SS,Lat,NS,Lon,EW,TZ,City,Country
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        lines = ["Name,Day,Month,Year,Hour,Min,Sec,Lat,NS,Lon,EW,TZ,City,Country"]
        for r in records:
            lat_d, lat_m, _ = _dms(r.latitude)
            lon_d, lon_m, _ = _dms(r.longitude)
            ns = "N" if r.latitude >= 0 else "S"
            ew = "E" if r.longitude >= 0 else "W"
            tz = f"{r.timezone_offset:+.2f}"

            def q(s: str) -> str:
                return f'"{s}"' if "," in s else s

            lines.append(
                f"{q(r.name)},{r.day},{r.month},{r.year},"
                f"{r.hour},{r.minute},{r.second},"
                f"{lat_d}:{lat_m},{ns},"
                f"{lon_d}:{lon_m},{ew},"
                f"{tz},{q(r.city)},{q(r.country)}"
            )

        output_path.write_text("\n".join(lines), encoding="utf-8")
        return output_path
