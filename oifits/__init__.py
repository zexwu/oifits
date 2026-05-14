from .oi_array import OI_ARRAY, BSL2TEL, TRI2BSL
from .oi_vis import OI_VIS
from .oi_vis2 import OI_VIS2
from .oi_wavelength import OI_WAVELENGTH
from .oi_t3 import OI_T3
from .oi_flux import OI_FLUX
from .oi import OI
from . import utils

__version__ = "0.1.1"

GRAVITY_FT = 20
GRAVITY_FT_P1 = 21
GRAVITY_FT_P2 = 22

GRAVITY_SC = 10
GRAVITY_SC_P1 = 11
GRAVITY_SC_P2 = 12

__all__ = [
    "OI_ARRAY",
    "BSL2TEL",
    "TRI2BSL",
    "OI_VIS",
    "OI_VIS2",
    "OI_WAVELENGTH",
    "OI_T3",
    "OI_FLUX",
    "OI",
    "utils",
]
