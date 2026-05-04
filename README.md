# Sun Live

This project downloads and stores near real-time solar observations from:

* **NASA SDO (Solar Dynamics Observatory)** - AIA and HMI imagery
* **NOAA DSCOVR spacecraft** - Solar wind plasma and magnetic field data

It provides a simple pipeline to fetch, normalize, and save solar data locally for analysis or visualization.

---

## Features

* Downloads multi-wavelength solar images from SDO AIA
* Fetches solar magnetic field (HMI magnetogram)
* Retrieves DSCOVR 2-hour solar wind plasma data
* Retrieves DSCOVR interplanetary magnetic field (IMF) data
* Converts data into:

  * JPEG images (solar observations)
  * CSV time-series files (space weather data)
* Returns a unified structured JSON-like output

---

## Data Sources

### SDO (NASA / JSOC Stanford)

* AIA EUV images (multiple wavelengths)
* HMI magnetograms (line-of-sight magnetic field)

### DSCOVR (NOAA SWPC)

* Solar wind plasma: density, speed, temperature
* Magnetic field: IMF components (Bx, By, Bz)

---

## Project Structure

Main functionality is contained in a single module with three core fetchers:

### 1. `fetch_aia(output_dir)`

Downloads AIA solar images at multiple wavelengths:

Supported wavelengths:

```
94, 131, 171, 193, 211, 304, 335, 1600 Å
```

**Output:**

* Saves images as `.jpg`
* Returns dictionary mapping wavelength → file path

---

### 2. `fetch_hmi(output_dir)`

Downloads the latest HMI magnetogram image.

**Output:**

* `hmi_m.jpg`

---

### 3. `fetch_sensors(output_dir)`

Downloads DSCOVR space weather data:

#### IMF (Magnetic Field)

Saved as:

```
imf.csv
```

Columns include:

* bx_gsm
* by_gsm
* bz_gsm
* bt
* lat_gsm
* lon_gsm
* timestamp

#### Plasma

Saved as:

```
plasma.csv
```

Columns include:

* density
* speed
* temperature
* timestamp

Also returns latest values:

```python
Bx, By, Bz, V, N, T
```

---

### 4. `fetch_all(output_dir)`

Runs the full pipeline:

* AIA images
* HMI magnetogram
* DSCOVR plasma + magnetic field

**Returns:**

```python
{
    "timestamp": ISO time,
    "sensors": {...},
    "aia": {...},
    "hmi": {...}
}
```

---

## Installation

### Requirements

Install dependencies:

```bash
pip install requests pandas pillow
```

---

## Usage Example

```python
from pathlib import Path

from sun_live import fetch_all

output_dir = Path("data")

result = fetch_all(output_dir)

print(result["sensors"]["Bz"])
print(result["hmi"]["hmi_m"])
print(result["aia"]["171"])
```

---

## Output Directory Structure

After running, you will get:

```
data/
│
├── aia94.jpg
├── aia131.jpg
├── aia171.jpg
├── aia193.jpg
├── aia211.jpg
├── aia304.jpg
├── aia335.jpg
├── aia1600.jpg
│
├── hmi_m.jpg
│
├── imf.csv
└── plasma.csv
```

---

## Notes

* Data is fetched in real-time from public NOAA/NASA endpoints.
* Network errors will raise exceptions if servers are unavailable.
* Images are converted to JPEG if needed for consistency.
* Timestamping is based on local execution time (`datetime.now()`).

---

