"""
Paperclip — Astrological Data Pipeline

Reads Excel/CSV files containing birth data and converts them to formats
accepted by Solar Fire, Astral Gold (iOS), Parashara's Light 9, and
JyotisharSoftware 9.
"""
from .reader import BirthDataReader
from .converter import AstroConverter

__all__ = ["BirthDataReader", "AstroConverter"]
