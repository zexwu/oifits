from __future__ import annotations
from .base import HDUModel
from numpy.typing import NDArray
from typing import Optional


class OI_FLUX(HDUModel):
    EXTNAME = "OI_FLUX"
    COLUMNS = [
        ("STA_INDEX", True),
        ("MJD", True),
        ("FLAG", True),
        ("FLUX", True), ("FLUXERR", True),
    ]

    sta_index: NDArray
    mjd: NDArray

    flag: NDArray
    flux: NDArray
    fluxerr: NDArray

    def _post_decode(self) -> None:
        return
