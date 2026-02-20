from __future__ import annotations
from .base import HDUModel


class OI_WAVELENGTH(HDUModel):
    EXTNAME = "OI_WAVELENGTH"
    COLUMNS = [
        ("EFF_WAVE", True),
        ("EFF_BAND", False),
    ]

    def _post_decode(self) -> None:
        return
