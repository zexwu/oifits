from __future__ import annotations
from .base import HDUModel
from numpy.typing import NDArray
from typing import Optional

import numpy as np


class OI_ARRAY(HDUModel):
    EXTNAME = "OI_ARRAY"
    COLUMNS = [
        ("STA_INDEX", True),
        ("STA_NAME", True),
        ("STAXYZ", True),
        ("TEL_NAME", False),
        ("DIAMETER", False),
        ("FOV", False),
        ("FOVTYPE", False),
    ]

    sta_index: NDArray
    sta_name: NDArray
    staxyz: NDArray

    tel_name: Optional[NDArray]

    diameter: Optional[NDArray]
    fov: Optional[NDArray]
    fovtype: Optional[NDArray]

    def _post_decode(self) -> None:
        self.sta_name = np.char.strip(self.sta_name)
        if self.tel_name is not None:
            self.tel_name = np.char.strip(self.tel_name)
