from __future__ import annotations
from .base import HDUModel
from numpy.typing import NDArray
from typing import Optional

import numpy as np


class OI_T3(HDUModel):
    EXTNAME = "OI_T3"
    COLUMNS = [
        ("MJD", True),
        ("TIME", True),
        ("INT_TIME", True),
        ("T3AMP", True), ("T3AMPERR", True),
        ("T3PHI", True), ("T3PHIERR", True),
        ("U1COORD", True), ("V1COORD", True),
        ("U2COORD", True), ("V2COORD", True),
        ("STA_INDEX", True),
        ("FLAG", True),
        ("CORRINDX_T3AMP", False),
        ("CORRINDX_T3PHI", False),
    ]

    mjd: NDArray
    time: NDArray
    int_time: NDArray
    t3phi: NDArray
    t3phierr: NDArray
    t3amp: NDArray
    t3amperr: NDArray
    u1coord: NDArray
    v1coord: NDArray
    u2coord: NDArray
    v2coord: NDArray
    sta_index: NDArray
    flag: NDArray

    corrindx_t3amp: Optional[NDArray] = None
    corrindx_t3phi: Optional[NDArray] = None

    # User defined attributes
    n_tri: Optional[int] = None
    n_dit: Optional[int] = None

    def _post_decode(self) -> None:
        self.n_tri = len(np.unique(self.sta_index, axis=0))
        self.n_dit = self.mjd.shape[0] // self.n_tri

        if self.n_tri * self.n_dit != self.mjd.shape[0]:
            raise ValueError("Data length must be divisible by n_tri to determine n_dit")
        return

    def reshape(self) -> None:
        """Reshape time-ordered rows into [n_dit, n_tri, ...] grids."""
        if self.n_tri is None or self.n_dit is None:
            raise ValueError("Call after _post_decode; n_tri/n_dit not set")

        to_reshape = ["mjd", "time", "int_time", "t3phi", "t3phierr", "t3amp", "t3amperr",
                      "u1coord", "v1coord", "u2coord", "v2coord", "flag"]
        for attr in to_reshape:
            attr_value = getattr(self, attr, None)
            if attr_value is None: continue
            if attr_value.shape[0] != self.n_tri * self.n_dit:
                raise ValueError(f"Data length of {attr} must be n_tri * n_dit")
            if attr_value.ndim == 1:
                setattr(self, attr, attr_value.reshape(self.n_dit, self.n_tri))
            else:
                setattr(self, attr, attr_value.reshape(self.n_dit, self.n_tri, -1))

    __doc__ = """Triple product table decoder (``OI_T3``).

    Provides closure phase (`t3phi`) and amplitude (`t3amp`) data with
    associated errors and baseline coordinates.
    """
