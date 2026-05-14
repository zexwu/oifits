from __future__ import annotations
from .base import HDUModel, ReshapeMixin
from numpy.typing import NDArray
from typing import Self

import numpy as np


class OI_FLUX(HDUModel, ReshapeMixin):
    EXTNAME = "OI_FLUX"
    COLUMNS = [
        ("MJD", True),
        ("INT_TIME", True),
        ("FLUX", False),
        ("FLUXDATA", False),
        ("FLUXERR", True),
        ("FLAG", True),
        ("STA_INDEX", False),
        ("CORRINDX_FLUXDATA", False),
    ]

    mjd: NDArray
    int_time: NDArray

    flux: NDArray | None
    fluxdata: NDArray | None
    fluxerr: NDArray
    flag: NDArray
    sta_index: NDArray | None
    corrindx_fluxdata: NDArray | None

    n_tel: int
    n_dit: int

    def _post_decode(self) -> None:
        n_tri = len(np.unique(self.sta_index, axis=0))
        n_dit = self.mjd.shape[0] // n_tri
        if n_tri * n_dit != self.mjd.shape[0]:
            raise ValueError(
                "Data length must be divisible by n_tel to determine n_dit"
            )
        self.n_tel = int(n_tri)
        self.n_dit = int(n_dit)
        return

    def reshape(self, *, inplace: bool = True) -> Self:
        """In-place reshape into [n_dit, n_tel, ...] grids."""
        fields = [i[0].lower() for i in self.COLUMNS]
        self._reshape_fields(fields, self.n_dit, self.n_tel, inplace=inplace)
        return self

    def flatten(self, *, inplace: bool = True) -> Self:
        """Flatten reshaped fields back into row-major (nrow, ...) arrays."""
        fields = [i[0].lower() for i in self.COLUMNS]
        self._flatten_fields(fields, self.n_dit, self.n_tel, inplace=inplace)
        return self

    def __getitem__(self, item) -> Self:
        fields = [i[0].lower() for i in self.COLUMNS]
        for field in fields:
            if getattr(self, field) is not None:
                setattr(self, field, getattr(self, field)[item])
        return self

    __doc__ = """Flux table decoder (``OI_FLUX``).

    Decodes station-indexed fluxes and errors per channel for a given EXTVER.
    """
