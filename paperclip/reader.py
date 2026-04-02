"""
BirthDataReader — reads Excel/CSV files containing astrological birth data.

Expected columns (case-insensitive, flexible naming):
  name         — person's name
  date         — birth date (various formats accepted)
  time         — birth time (HH:MM or HH:MM:SS)
  city/place   — birth city/location
  country      — birth country
  latitude     — decimal degrees (N positive, S negative)
  longitude    — decimal degrees (E positive, W negative)
  timezone/tz  — UTC offset (e.g. "-5.0", "IST", "America/New_York")
  notes        — optional notes
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd


@dataclass
class BirthRecord:
    """Normalized birth data for a single chart."""
    name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int = 0
    city: str = ""
    country: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    # UTC offset in decimal hours (e.g. -5.5 for IST-like, +5.5 for IST)
    timezone_offset: float = 0.0
    timezone_name: str = ""
    notes: str = ""

    @property
    def date_str(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d}"

    @property
    def time_str(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}:{self.second:02d}"

    @property
    def lat_str(self) -> str:
        """Degrees-minutes format with N/S indicator."""
        deg = abs(self.latitude)
        d = int(deg)
        m = (deg - d) * 60
        ns = "N" if self.latitude >= 0 else "S"
        return f"{d:02d}°{m:04.1f}'{ns}"

    @property
    def lon_str(self) -> str:
        """Degrees-minutes format with E/W indicator."""
        deg = abs(self.longitude)
        d = int(deg)
        m = (deg - d) * 60
        ew = "E" if self.longitude >= 0 else "W"
        return f"{d:03d}°{m:04.1f}'{ew}"


# Column name aliases — maps common variations → canonical field name
_COLUMN_ALIASES: dict[str, str] = {
    # name
    "name": "name", "full name": "name", "person": "name", "native": "name",
    "chart name": "name", "subject": "name",
    # date
    "date": "date", "birth date": "date", "dob": "date", "birthdate": "date",
    "date of birth": "date",
    # time
    "time": "time", "birth time": "time", "tob": "time", "birthtime": "time",
    "time of birth": "time",
    # city/place
    "city": "city", "place": "city", "birth place": "city", "birthplace": "city",
    "location": "city", "town": "city", "birth city": "city",
    # country
    "country": "country",
    # lat/lon
    "latitude": "latitude", "lat": "latitude",
    "longitude": "longitude", "lon": "longitude", "long": "longitude",
    # timezone
    "timezone": "timezone", "tz": "timezone", "time zone": "timezone",
    "utc offset": "timezone", "gmt offset": "timezone", "utc+": "timezone",
    # notes
    "notes": "notes", "note": "notes", "remarks": "notes", "comments": "notes",
}


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename DataFrame columns to canonical names."""
    rename_map = {}
    for col in df.columns:
        key = col.strip().lower()
        if key in _COLUMN_ALIASES:
            rename_map[col] = _COLUMN_ALIASES[key]
    return df.rename(columns=rename_map)


def _parse_date(val) -> tuple[int, int, int]:
    """Parse a date value into (year, month, day)."""
    if pd.isna(val):
        raise ValueError("Missing date")
    if hasattr(val, "year"):
        return int(val.year), int(val.month), int(val.day)
    s = str(val).strip()
    # Try common patterns
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%d.%m.%Y",
                "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"):
        try:
            from datetime import datetime
            dt = datetime.strptime(s, fmt)
            return dt.year, dt.month, dt.day
        except ValueError:
            continue
    # Try pandas parser as fallback
    try:
        dt = pd.to_datetime(s, dayfirst=True)
        return int(dt.year), int(dt.month), int(dt.day)
    except Exception:
        pass
    raise ValueError(f"Cannot parse date: {val!r}")


def _parse_time(val) -> tuple[int, int, int]:
    """Parse a time value into (hour, minute, second)."""
    if pd.isna(val):
        return 12, 0, 0  # noon default when time unknown
    if hasattr(val, "hour"):
        return int(val.hour), int(val.minute), int(val.second)
    s = str(val).strip()
    # Handle HH:MM:SS or HH:MM
    m = re.match(r"^(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*(AM|PM))?$", s, re.IGNORECASE)
    if m:
        h, mn, sc = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
        ampm = m.group(4)
        if ampm:
            if ampm.upper() == "PM" and h < 12:
                h += 12
            elif ampm.upper() == "AM" and h == 12:
                h = 0
        return h, mn, sc
    raise ValueError(f"Cannot parse time: {val!r}")


def _parse_tz(val) -> tuple[float, str]:
    """Parse timezone into (offset_decimal_hours, name)."""
    if pd.isna(val):
        return 0.0, "UTC"
    s = str(val).strip()
    # Numeric offset like "+5.5" or "-5" or "5:30"
    m = re.match(r"^([+-]?\d+)(?:[:\.](\d+))?$", s)
    if m:
        h = int(m.group(1))
        frac = int(m.group(2) or 0)
        # Treat fractional part as minutes if > 1, else as decimal hours fraction
        offset = h + (frac / 60 if frac > 1 else frac * 0.1 * (1 if h >= 0 else -1))
        return offset, s
    # Named zones — approximate offsets for common astrology zones
    named = {
        "IST": 5.5, "GMT": 0.0, "UTC": 0.0, "EST": -5.0, "EDT": -4.0,
        "CST": -6.0, "CDT": -5.0, "MST": -7.0, "MDT": -6.0,
        "PST": -8.0, "PDT": -7.0, "CET": 1.0, "CEST": 2.0,
        "JST": 9.0, "AEST": 10.0, "AEDT": 11.0, "NZST": 12.0,
    }
    upper = s.upper()
    if upper in named:
        return named[upper], s
    # Try pytz if available
    try:
        import pytz
        from datetime import datetime
        tz = pytz.timezone(s)
        offset_td = tz.utcoffset(datetime(2000, 1, 1))
        offset_hours = offset_td.total_seconds() / 3600
        return offset_hours, s
    except Exception:
        pass
    return 0.0, s  # default UTC with original string as name


class BirthDataReader:
    """
    Read birth data from Excel (.xlsx, .xls) or CSV files.

    Usage:
        reader = BirthDataReader()
        records = reader.read("charts.xlsx")
        # records is a list[BirthRecord]
    """

    def read(self, path: str | Path) -> list[BirthRecord]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = path.suffix.lower()
        if suffix in (".xlsx", ".xls"):
            df = pd.read_excel(path, dtype=str)
        elif suffix == ".csv":
            df = pd.read_csv(path, dtype=str)
        else:
            raise ValueError(f"Unsupported file format: {suffix}. Use .xlsx, .xls, or .csv")

        df = _normalize_columns(df)
        df = df.where(pd.notna(df), None)  # replace NaN with None

        records: list[BirthRecord] = []
        for idx, row in df.iterrows():
            try:
                record = self._parse_row(row, idx)
                records.append(record)
            except Exception as e:
                print(f"Warning: skipping row {idx + 2}: {e}")

        return records

    def _parse_row(self, row: pd.Series, idx: int) -> BirthRecord:
        name = str(row.get("name") or f"Chart_{idx + 1}").strip()

        year, month, day = _parse_date(row.get("date"))
        hour, minute, second = _parse_time(row.get("time"))

        city = str(row.get("city") or "").strip()
        country = str(row.get("country") or "").strip()

        lat = row.get("latitude")
        lon = row.get("longitude")
        try:
            latitude = float(lat) if lat is not None else 0.0
            longitude = float(lon) if lon is not None else 0.0
        except (ValueError, TypeError):
            latitude = longitude = 0.0

        tz_offset, tz_name = _parse_tz(row.get("timezone"))
        notes = str(row.get("notes") or "").strip()

        return BirthRecord(
            name=name,
            year=year, month=month, day=day,
            hour=hour, minute=minute, second=second,
            city=city, country=country,
            latitude=latitude, longitude=longitude,
            timezone_offset=tz_offset, timezone_name=tz_name,
            notes=notes,
        )
