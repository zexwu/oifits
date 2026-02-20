from .oi_array import OI_ARRAY
from .oi_vis import OI_VIS
from .oi_wavelength import OI_WAVELENGTH
from .oi_t3 import OI_T3
from .oi_flux import OI_FLUX
from .oi import OI

__all__ = [
    "OI_ARRAY",
    "OI_VIS",
    "OI_WAVELENGTH",
    "OI_T3",
    "OI_FLUX",
    "OI",
    "GRAVITY_FT",
    "GRAVITY_FT_P1",
    "GRAVITY_FT_P2",
    "GRAVITY_SC",
    "GRAVITY_SC_P1",
    "GRAVITY_SC_P2",
    "__version__",
]

__version__ = "0.1.0"

GRAVITY_FT = 20
GRAVITY_FT_P1 = 21
GRAVITY_FT_P2 = 22

GRAVITY_SC = 10
GRAVITY_SC_P1 = 11
GRAVITY_SC_P2 = 12
