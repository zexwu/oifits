from __future__ import annotations
from .base import HDUModel
from numpy.typing import NDArray
from typing import Optional


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

    mjd: NDArray

    sta_index: NDArray
    ucoord: NDArray
    vcoord: NDArray

    flag: NDArray

    visdata: NDArray
    viserr: NDArray

    visamp: NDArray
    visamperr: NDArray

    visphi: Optional[NDArray]
    visphierr: Optional[NDArray]

    def _post_decode(self) -> None:
        return
