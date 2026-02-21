from __future__ import annotations

import numpy as np
from numpy.typing import NDArray
from typing import Optional

from .base import HDUModel


class OI_VIS2(HDUModel):
    EXTNAME = "OI_VIS2"
    COLUMNS = [
        ("TIME", True),
        ("MJD", True),
        ("INT_TIME", True),
        ("VIS2DATA", True),
        ("VIS2ERR", True),
        ("UCOORD", True),
        ("VCOORD", True),
        ("STA_INDEX", True),
        ("FLAG", True),
        ("CORRINDX_VIS2DATA", False),
    ]

    time: NDArray
    mjd: NDArray
    int_time: NDArray
    vis2data: NDArray
    vis2err: NDArray
    ucoord: NDArray
    vcoord: NDArray
    sta_index: NDArray
    flag: NDArray

    corrindx_vis2data: Optional[NDArray]

    # Derived shapes
    n_bsl: Optional[int] = None
    n_dit: Optional[int] = None

    def _post_decode(self) -> None:
        self.n_bsl = len(np.unique(self.sta_index, axis=0))
        self.n_dit = self.mjd.shape[0] // self.n_bsl
        if self.n_bsl * self.n_dit != self.mjd.shape[0]:
            raise ValueError("Data length must be divisible by n_bsl to determine n_dit")
        return

    def reshape(self) -> None:
        """Reshape time-ordered rows into [n_dit, n_bl, ...] grids."""
        if self.n_bsl is None or self.n_dit is None:
            raise ValueError("Call after _post_decode; n_bsl/n_dit not set")

        to_reshape = ["time", "mjd", "int_time", "vis2data", "vis2err",
                      "ucoord", "vcoord", "flag"]
        for attr in to_reshape:
            attr_value = getattr(self, attr, None)
            if attr_value is None: continue
            if attr_value.shape[0] != self.n_bsl * self.n_dit:
                raise ValueError(f"Data length of {attr} must be n_bsl * n_dit")
            if attr_value.ndim == 1:
                setattr(self, attr, attr_value.reshape(self.n_dit, self.n_bsl))
            else:
                setattr(self, attr, attr_value.reshape(self.n_dit, self.n_bsl, -1))

    __doc__ = """Squared visibility table decoder (``OI_VIS2``).

    Fields map directly to OIFITS binary table columns. See class attributes for
    available columns and the instance properties for numpy arrays.
    """
