from __future__ import annotations

from .base import HDUModel


class OI_VIS(HDUModel):
    EXTNAME = "OI_VIS"
    COLUMNS = [
        ("MJD", True),
        ("STA_INDEX", True),
        ("UCOORD", True), ("VCOORD", True),
        ("FLAG", True),
        ("VISDATA", True), ("VISERR", True),
        ("VISAMP", True), ("VISAMPERR", True),
        ("VISPHI", False), ("VISPHIERR", False),
    ]

    def _post_decode(self) -> None:
        return
