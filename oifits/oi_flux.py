from __future__ import annotations
from .base import HDUModel


class OI_FLUX(HDUModel):
    EXTNAME = "OI_FLUX"
    COLUMNS = [
        ("STA_INDEX", True),
        ("MJD", True),
        ("FLAG", True),
        ("FLUX", True), ("FLUXERR", True),
    ]

    def _post_decode(self) -> None:
        return
