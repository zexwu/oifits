from __future__ import annotations
from typing import Any, ClassVar, Optional, Sequence, Tuple, Iterable, Mapping
from collections.abc import Sequence as SeqABC
from types import MappingProxyType

import numpy as np
from astropy.io import fits


def require_extname(hdul: fits.HDUList, name: str) -> None:
    target = name.strip().upper()
    for h in hdul:
        ext = (h.header.get("EXTNAME") or h.name or "").strip().upper()
        if ext == target:
            return
    raise KeyError(f"Missing HDU EXTNAME={target}")


def header_whitelist(hdr: fits.Header, keys: Iterable[str]) -> dict[str, Any]:
    KU = {k.upper() for k in keys}
    return {k: hdr.get(k) for k in hdr.keys() if k.upper() in KU}


class HDUModel:
    """Base class for EXTNAME-named binary table HDUs.

    Subclasses define ``EXTNAME`` and ``COLUMNS`` (name, required) and gain
    lower-case attributes for each column (e.g. ``STA_INDEX`` -> ``sta_index``).
    """

    EXTNAME: ClassVar[str]
    COLUMNS: ClassVar[Sequence[Tuple[str, bool]]] = ()

    # common metadata
    header: dict[str, Any]

    extver: Optional[int]
    insname: Optional[str]
    arrname: Optional[str]


    def __init__(
        self,
        hdul: fits.HDUList,
        extver: Optional[int] = None,
        header_keys: Optional[list[str]] = None,
    ) -> None:
        require_extname(hdul, self.EXTNAME)

        if extver is None:
            hdu = hdul[self.EXTNAME]
        else:
            hdu = hdul[(self.EXTNAME, extver)]
        hdr = hdu.header
        data = hdu.data

        default_keys = ["EXTNAME", "EXTVER", "INSNAME", "ARRNAME", "DATE-OBS", "OBJECT", "FRAME"]
        keys = default_keys if header_keys is None else header_keys
        self.header = MappingProxyType(header_whitelist(hdr, keys))

        self.extver = int(hdr.get("EXTVER", 1))
        self.insname = hdr.get("INSNAME")
        self.arrname = hdr.get("ARRNAME")

        # columns
        for colname, required in self.COLUMNS:
            attr = colname.lower()
            if colname in data.names:
                setattr(self, attr, np.asarray(data[colname]))
            elif required:
                raise KeyError(f"Missing column {colname} in {self.EXTNAME}")
            else:
                setattr(self, attr, None)

        self._post_decode()

    def _post_decode(self) -> None:
        """Subclass hook for value cleanup/validation after decode."""
        return

    # Properties for common metadata; MappingProxyType keeps header read-only.
    @property
    def metadata(self) -> Mapping[str, Any]:
        """Immutable header subset (EXTNAME/EXTVER/INSNAME/ARRNAME etc.)."""
        return self.header

    @property
    def extver_id(self) -> Optional[int]:
        """Alias for ``EXTVER`` header value."""
        return self.extver

    def __repr__(self) -> str:
        parts: list[str] = []

        # identity
        parts.append(f"{self.__class__.__name__}(")

        # header-like identifiers
        for attr in ["extver", "insname", "arrname"]:
            parts.append(f"  {attr:10s}= {getattr(self, attr)!r},")

        # columns: show dtype/shape only
        for colname, _required in self.COLUMNS:
            attr = colname.lower()
            v: Any = getattr(self, attr, None)
            if v is None:
                # parts.append(f"  {attr:10s}= None,")
                continue

            a = np.asarray(v)
            # if a.dtype.kind in ("U", "S", "O") and a.ndim == 1 and a.size <= 8:
            if a.ndim == 1 and a.size <= 8:
                # short string lists: show a few values
                parts.append(f"  {attr:10s}= {a!r},")
            else:
                shape = str(a.shape)+ ","
                dtype = "'" + str(a.dtype) + "'"
                parts.append(f"  {attr:10s}= array(shape={shape:10s}dtype={dtype:6s}),")

        parts.append(")")

        return "\n".join(parts)


class ReshapeMixin:
    """Shared helper for reshaping time-ordered rows into [outer, inner, ...] grids."""

    def _reshape_fields(
        self,
        fields: SeqABC[str],
        outer: int,
        inner: int,
        *,
        inplace: bool = True,
    ) -> dict[str, np.ndarray]:
        result: dict[str, np.ndarray] = {}
        for name in fields:
            value = getattr(self, name, None)
            if value is None: continue
            arr = np.asarray(value)

            # idempotent: already shaped as (outer, inner, ...)
            if arr.ndim >= 2 and arr.shape[0] == outer and arr.shape[1] == inner:
                reshaped = arr
            else:
                if arr.shape[0] != outer * inner:
                    raise ValueError(f"Data length of {name} must be {outer} * {inner}")
                tail = arr.shape[1:]
                shape = (outer, inner, *tail) if tail else (outer, inner)
                reshaped = arr.reshape(shape)

            if inplace: setattr(self, name, reshaped)
            result[name] = reshaped
        return result
