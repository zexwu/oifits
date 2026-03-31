from __future__ import annotations
from .base import HDUModel, ReshapeMixin
from numpy.typing import NDArray
from typing import Optional, Self
import numpy as np


class OI_VIS(HDUModel, ReshapeMixin):
    EXTNAME = "OI_VIS"
    COLUMNS = [
        ("TIME", True),
        ("MJD", True),
        ("INT_TIME", True),
        ("VISAMP", False), ("VISAMPERR", False),
        ("VISPHI", False), ("VISPHIERR", False),
        ("UCOORD", True), ("VCOORD", True),
        ("STA_INDEX", True),
        ("FLAG", True),
        ("VISDATA", False), ("VISERR", False),
        ("CORRINDX_VISAMP", False),
        ("CORRINDX_VISPHI", False),

        # ("V_FACTOR", False),
        # ("GDELAY", False),
        # ("GDELAY_BOOT", False),
        # ("GDELAY_FT", False),
        # ("FIRST_FT", False), ("LAST_FT", False),
        # ("FIRST_MET", False), ("LAST_MET", False)

    ]

    time: NDArray
    mjd: NDArray
    int_time: NDArray
    visamp: NDArray
    visamperr: NDArray
    visphi: NDArray
    visphierr: NDArray
    ucoord: NDArray
    vcoord: NDArray
    sta_index: NDArray
    flag: NDArray

    visdata: Optional[NDArray]
    viserr: Optional[NDArray]
    corrindx_visamp: Optional[NDArray]
    corrindx_visphi: Optional[NDArray]

    # v_factor: Optional[NDArray]
    # gdelay: Optional[NDArray] = None
    # gdelay_boot: Optional[NDArray] = None
    # gdelay_ft: Optional[NDArray] = None
    # first_ft: Optional[NDArray] = None
    # last_ft: Optional[NDArray] = None
    # first_met: Optional[NDArray] = None
    # last_met: Optional[NDArray] = None

    # Derived shapes
    n_bsl: int = 0
    n_dit: int = 0

    def _post_decode(self) -> None:
        # infer number of baselines and dithers (DITs)
        self.n_bsl = len(np.unique(self.sta_index, axis=0))
        self.n_dit = self.mjd.shape[0] // self.n_bsl
        if self.n_bsl * self.n_dit != self.mjd.shape[0]:
            raise ValueError("Data length must be divisible by n_bsl to determine n_dit")
        self.ucoord = self.ucoord.astype(np.float64)
        self.vcoord = self.vcoord.astype(np.float64)
        return

    def reshape(self, *, inplace: bool = True) -> Self:
        """In-place reshape into [n_dit, n_bsl, ...] grids."""
        fields = [i[0].lower() for i in self.COLUMNS]
        self._reshape_fields(fields, self.n_dit, self.n_bsl, inplace=inplace)
        return self

    def flatten(self, *, inplace: bool = True) -> Self:
        """Flatten reshaped fields back into row-major (nrow, ...) arrays."""
        fields = [i[0].lower() for i in self.COLUMNS]
        self._flatten_fields(fields, self.n_dit, self.n_bsl, inplace=inplace)
        return self

    def __getitem__(self, item) -> Self:
        fields = [i[0].lower() for i in self.COLUMNS]
        for field in fields:
            if getattr(self, field) is not None:
                setattr(self, field, getattr(self, field)[item])
        return self


    __doc__ = """Visibility table decoder (``OI_VIS``).

    Fields map directly to OIFITS binary table columns. See class attributes for
    available columns and the instance properties for numpy arrays.
    """
