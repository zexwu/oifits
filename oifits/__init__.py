from dataclasses import dataclass

from astropy.io.fits import HDUList

from .oi_array import OI_ARRAY
from .oi_flux import OI_FLUX
from .oi_t3 import OI_T3
from .oi_vis import OI_VIS
from .oi_wavelength import OI_WAVELENGTH

GRAVITY_FT = 20
GRAVITY_FT_P1 = 21
GRAVITY_FT_P2 = 22

GRAVITY_SC = 10
GRAVITY_SC_P1 = 11
GRAVITY_SC_P2 = 12


@dataclass(slots=True)
class OI:
    array: OI_ARRAY
    wavelength: OI_WAVELENGTH
    flux: OI_FLUX
    vis: OI_VIS
    t3: OI_T3
    extver: int

    @classmethod
    def load(cls, hdul: HDUList, extver: int):
        return cls(
            array=OI_ARRAY(hdul),
            wavelength=OI_WAVELENGTH(hdul, extver),
            flux=OI_FLUX(hdul, extver),
            vis=OI_VIS(hdul, extver),
            t3=OI_T3(hdul, extver),
            extver=extver,
        )
