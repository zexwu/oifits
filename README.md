# oifits

A minimal Python library for reading OIFITS files with **explicit EXTVER selection semantics**.

The library is designed for scientific analysis workflows (not pipeline reduction) where the user needs a *self-consistent interferometric dataset* extracted from multi-extension OIFITS files — in particular VLTI/GRAVITY data products.

This is **not** a general-purpose OIFITS abstraction layer and intentionally avoids heavy object hierarchies, automatic merging, or implicit data association.

Instead, the core concept is simple:

> An `OI` object represents one selected interferometric dataset defined by a single `EXTVER`.

## Quick Start

```python
from astropy.io import fits
from oifits import OI, GRAVITY_SC

hdul = fits.open("gravity_file.fits")

oi = OI.load(hdul, GRAVITY_SC)

print(oi.vis.visamp.shape)
print(oi.t3.t3phi.shape)
print(oi.wavelength.eff_wave)
```

The object `oi` now contains a single consistent interferometric dataset.

---

## What the Library Does

* Reads OIFITS tables into typed Python objects
* Copies FITS columns into numpy arrays
* Keeps relevant header metadata
* Provides predictable selection behavior

---

## Object Model

```
OI
 ├── vis        -> OI_VIS
 ├── t3         -> OI_T3
 ├── flux       -> OI_FLUX
 ├── wavelength -> OI_WAVELENGTH
 └── array      -> OI_ARRAY
```

Each table class is a thin decoder around a FITS `BinTableHDU`.
