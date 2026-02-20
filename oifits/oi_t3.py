from __future__ import annotations
from .base import HDUModel


class OI_T3(HDUModel):
    EXTNAME = "OI_T3"
    COLUMNS = [
        ("MJD", True),
        ("STA_INDEX", True),
        ("U1COORD", True), ("V1COORD", True),
        ("U2COORD", True), ("V2COORD", True),
        ("FLAG", True),
        ("T3PHI", True), ("T3PHIERR", True),
        ("T3AMP", False), ("T3AMPERR", False),
    ]

    def _post_decode(self) -> None:
        return
