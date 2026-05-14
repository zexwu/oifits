from __future__ import annotations
from .base import HDUModel
from numpy.typing import NDArray


class OI_WAVELENGTH(HDUModel):
    EXTNAME = "OI_WAVELENGTH"
    COLUMNS = [
        ("EFF_WAVE", True),
        ("EFF_BAND", False),
    ]

    eff_wave: NDArray
    eff_band: NDArray | None

    n_wave: int = 0

    def _post_decode(self) -> None:
        self.n_wave = self.eff_wave.shape[0]
        self.eff_wave = self.eff_wave.astype(float)

        return

    __doc__ = """Wavelength table decoder (``OI_WAVELENGTH``).

    Exposes effective wavelength (`eff_wave`) and optional bandpass (`eff_band`).
    """
