from typing import List, Tuple

import numpy as np
from numpy.typing import NDArray
from numba import njit

from .oi_t3 import OI_T3
from .oi_vis import OI_VIS
from .oi_vis2 import OI_VIS2
from .oi_wavelength import OI_WAVELENGTH

MAS2RAD = np.pi / (180 * 3600 * 1000)

@njit
def _phasor(ucoord: NDArray, vcoord: NDArray, eff_wave: NDArray, dra: float, ddec: float) -> NDArray:
    phi = -2 * np.pi * MAS2RAD * (ucoord * dra + vcoord * ddec)
    phi = phi[..., None] / eff_wave
    return np.exp(1j * phi)


def binary_visibility(oi_wave: OI_WAVELENGTH, oi_vis: OI_VIS|OI_VIS2, par: List) -> NDArray:
    dra, ddec, eta = par

    phasor = _phasor(oi_vis.ucoord, oi_vis.vcoord, oi_wave.eff_wave, dra, ddec)
    V = (1 + eta * phasor) / (1 + eta)
    return V


def binary_bispectrum(oi_wave: OI_WAVELENGTH, oi_t3: OI_T3, par: List) -> NDArray:
    dra, ddec, eta = par

    phasor1 = _phasor(oi_t3.u1coord, oi_t3.v1coord, oi_wave.eff_wave, dra, ddec)
    V1 = (1 + eta * phasor1) / (1 + eta)

    phasor2 = _phasor(oi_t3.u2coord, oi_t3.v2coord, oi_wave.eff_wave, dra, ddec)
    V2 = (1 + eta * phasor2) / (1 + eta)

    phasor3 = (phasor1 * phasor2).conj()
    V3 = (1 + eta * phasor3) / (1 + eta)

    return V1 * V2 * V3


def compute_gdelay(
    visdata: np.ndarray,
    wl: np.ndarray,
    search_range: Tuple[float, float] = (-100, 100),
    search_step: float = 0.1,
    n_newton: int = 5,
) -> np.ndarray:
    """
    Compute group delay for a batch of visibilities.

    Args:
        visdata: Visibility data array
        wl: Wavelength array
        search_range: Range for initial grid search
        n_newton: Number of Newton iterations for refinement

    Returns:
        Group delay values
    """
    # Constants
    k = -2j * np.pi / wl
    w = -2 * np.pi / wl

    # Initial grid search
    gd_grid = np.arange(search_range[0], search_range[1], search_step)
    phasors_grid = np.exp(gd_grid[:, None] * k[None, :])
    coherence = np.abs(np.tensordot(visdata, phasors_grid, axes=([-1], [-1])))

    idx_best = np.argmax(coherence, axis=-1)
    gd_current = gd_grid[idx_best]  # Shape: (N_frames,)

    # Newton-Raphson refinement
    for _ in range(n_newton):
        gd_exp = gd_current[:, None]
        rot_term = np.exp(1j * w * gd_exp)
        V_rot = visdata * rot_term

        S0 = np.sum(V_rot, axis=-1)
        S1 = np.sum(V_rot * (1j * w), axis=-1)
        S2 = np.sum(V_rot * (-(w**2)), axis=-1)

        S0_conj = np.conj(S0)
        grad = 2 * np.real(S1 * S0_conj)
        hess = 2 * np.real(S2 * S0_conj + S1 * np.conj(S1))

        diff = np.zeros_like(grad)
        mask = hess != 0
        diff[mask] = grad[mask] / hess[mask]

        gd_current = gd_current - diff

    return gd_current
