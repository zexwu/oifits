from __future__ import annotations
from .base import HDUModel
from numpy.typing import NDArray
from typing import Optional


class OI_FLUX(HDUModel):
    EXTNAME = "OI_FLUX"
    COLUMNS = [
        ("MJD", True),
        ("INT_TIME", True),
        ("FLUX", False), ("FLUXDATA", False), ("FLUXERR", True),
        ("FLAG", True),
        ("STA_INDEX", False),
        ("CORRINDX_FLUXDATA", False)
    ]

    mjd: NDArray
    int_time: NDArray

    flux: Optional[NDArray]
    fluxdata: Optional[NDArray]
    fluxerr: NDArray
    flag: NDArray
    sta_index: Optional[NDArray]
    corrindx_fluxdata: Optional[NDArray]

    def _post_decode(self) -> None:
        return

    __doc__ = """Flux table decoder (``OI_FLUX``).

    Decodes station-indexed fluxes and errors per channel for a given EXTVER.
    """
