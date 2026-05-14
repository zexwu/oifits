from collections.abc import Sequence
from copy import copy
from typing import TypeVar

import numpy as np
from numba import njit
from numpy.typing import NDArray

from . import OI_T3, OI_VIS, OI_VIS2, OI_WAVELENGTH

MAS2RAD = np.pi / (180 * 3600 * 1000)
T_OITable = TypeVar("T_OITable", OI_VIS, OI_VIS2, OI_T3)


@njit
def _phasor(ucoord: NDArray, vcoord: NDArray, eff_wave: NDArray, dra: float, ddec: float) -> NDArray:
    phi = -2 * np.pi * MAS2RAD * (ucoord * dra + vcoord * ddec)
    phi = phi[..., None] / eff_wave
    return np.exp(1j * phi)


def binary_visibility(oi_wave: OI_WAVELENGTH, oi_vis: OI_VIS | OI_VIS2, par: Sequence[float]) -> NDArray:
    dra, ddec, eta = par

    phasor = _phasor(oi_vis.ucoord, oi_vis.vcoord, oi_wave.eff_wave, dra, ddec)
    V = (1 + eta * phasor) / (1 + eta)
    return V


def binary_bispectrum(oi_wave: OI_WAVELENGTH, oi_t3: OI_T3, par: Sequence[float]) -> NDArray:
    dra, ddec, eta = par

    phasor1 = _phasor(oi_t3.u1coord, oi_t3.v1coord, oi_wave.eff_wave, dra, ddec)
    V1 = (1 + eta * phasor1) / (1 + eta)

    phasor2 = _phasor(oi_t3.u2coord, oi_t3.v2coord, oi_wave.eff_wave, dra, ddec)
    V2 = (1 + eta * phasor2) / (1 + eta)

    phasor3 = (phasor1 * phasor2).conj()
    V3 = (1 + eta * phasor3) / (1 + eta)

    return V1 * V2 * V3


def merge_frames(oi_table: T_OITable, *, inplace: bool = True) -> T_OITable:
    """Merge all DIT frames of an ``OI_VIS``, ``OI_VIS2``, or ``OI_T3`` table.

    The averaging follows GRAVI's ``gravi_average_vis`` algorithm: scalar
    coordinates/times use an unweighted mean, amplitudes use inverse-variance
    weights, phases use a weighted phasor mean in degrees, and flagged channels
    contribute with weight ``1e-19``. Columns not explicitly averaged are copied
    from the first frame group.
    """

    match oi_table:
        case OI_VIS():
            n_group = int(oi_table.n_bsl)
            value_cols = ("time", "mjd", "int_time", "ucoord", "vcoord")
            amp_cols = (("visamp", "visamperr"),)
            phi_cols = (("visphi", "visphierr"),)
        case OI_VIS2():
            n_group = int(oi_table.n_bsl)
            value_cols = ("time", "mjd", "int_time", "ucoord", "vcoord")
            amp_cols = (("vis2data", "vis2err"),)
            phi_cols = ()
        case OI_T3():
            n_group = int(oi_table.n_tri)
            value_cols = (
                "time",
                "mjd",
                "int_time",
                "u1coord",
                "v1coord",
                "u2coord",
                "v2coord",
            )
            amp_cols = (("t3amp", "t3amperr"),)
            phi_cols = (("t3phi", "t3phierr"),)
        case _:
            raise TypeError("oi_table must be an OI_VIS, OI_VIS2, or OI_T3 instance")

    n_dit = int(oi_table.n_dit)
    result = oi_table if inplace else copy(oi_table)
    if not inplace:
        for col, _required in result.COLUMNS:
            attr = col.lower()
            value = getattr(result, attr, None)
            if value is not None:
                setattr(result, attr, np.array(value, copy=True))
    if n_dit <= 1:
        return result

    def flat(name: str) -> NDArray:
        arr = np.asarray(getattr(result, name))
        if arr.shape[0] == n_dit * n_group:
            return arr
        if arr.ndim >= 2 and arr.shape[:2] == (n_dit, n_group):
            return arr.reshape(n_dit * n_group, *arr.shape[2:])
        raise ValueError(
            f"Column {name} has shape {arr.shape}; expected " f"({n_dit * n_group}, ...) or ({n_dit}, {n_group}, ...)"
        )

    columns: dict[str, NDArray] = {}
    for colname, _required in result.COLUMNS:
        attr = colname.lower()
        if getattr(result, attr, None) is not None:
            columns[attr] = flat(attr)
            setattr(result, attr, np.array(columns[attr][:n_group], copy=True))

    for attr in value_cols:
        if attr in columns:
            arr = columns[attr]
            setattr(result, attr, arr.reshape(-1, n_group, *arr.shape[1:]).mean(axis=0))

    with np.errstate(divide="ignore", invalid="ignore"):
        for data_attr, err_attr in amp_cols:
            if {data_attr, err_attr, "flag"} <= columns.keys():
                data = columns[data_attr].reshape(-1, n_group, *columns[data_attr].shape[1:])
                err = columns[err_attr].reshape(data.shape)
                flag = columns["flag"].reshape(data.shape)
                weight = np.where(flag, 1e-19, err**-2)
                weight_sum = weight.sum(axis=0)
                setattr(result, data_attr, (data * weight).sum(axis=0) / weight_sum)
                setattr(result, err_attr, weight_sum**-0.5)

        for phi_attr, err_attr in phi_cols:
            if {phi_attr, err_attr, "flag"} <= columns.keys():
                phi = columns[phi_attr].reshape(-1, n_group, *columns[phi_attr].shape[1:])
                err = columns[err_attr].reshape(phi.shape)
                flag = columns["flag"].reshape(phi.shape)
                weight = np.where(flag, 1e-19, err**-2)
                phasor = (np.exp(1j * np.deg2rad(phi)) * weight).sum(axis=0)
                setattr(result, phi_attr, np.rad2deg(np.angle(phasor)))
                setattr(result, err_attr, weight.sum(axis=0) ** -0.5)

    result._post_decode()
    return result


def compute_gdelay(
    visdata: np.ndarray,
    wl: np.ndarray,
    search_range: tuple[float, float] = (-100, 100),
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
