from __future__ import annotations
from .base import HDUModel
from numpy.typing import NDArray
from typing import Optional


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

    mjd: NDArray

    sta_index: NDArray
    u1coord: NDArray
    v1coord: NDArray
    u2coord: NDArray
    v2coord: NDArray

    flag: NDArray
    t3phi: NDArray
    t3phierr: NDArray
    t3amp: Optional[NDArray]
    t3amperr: Optional[NDArray]

    def _post_decode(self) -> None:
        return
