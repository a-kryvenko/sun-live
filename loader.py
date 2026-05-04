import requests
from datetime import datetime
from pathlib import Path
import pandas as pd
from PIL import Image
from io import BytesIO

SDO_AIA_LIVE_URL = "https://jsoc1.stanford.edu/data/aia/images/image_times"
AIA_WAVELENGTHS = [
    "94",
    "131",
    "171",
    "193",
    "211",
    "304",
    "335",
    "1600"
]

def fetch_aia(output_dir: Path, wavelengths: list[str] = AIA_WAVELENGTHS) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    r = requests.get(SDO_AIA_LIVE_URL)

    if r.status_code != 200:
        raise Exception("SDO server connection error: " + r.status_code)
    
    images = dict()
    for wave in wavelengths:
        images[wave] = ""
    
    for line in r.text.split("\n"):
        parts = line.split()
        if len(parts) == 2:
            try:
                if parts[0] in images:
                    response = requests.get(parts[1])
                    response.raise_for_status()

                    img = Image.open(BytesIO(response.content))

                    if img.format != "JPEG":
                        path = output_dir / f"aia{parts[0]}.jpg"
                        img.convert("RGB").save(path, "JPEG")
                    else:
                        ext = img.format.lower()
                        path = output_dir / f"aia{parts[0]}.{ext}"
                        path.write_bytes(response.content)

                    images[parts[0]] = path.as_posix()
                    
            except ValueError:
                pass

    return images

SDO_HMI_LIVE_ROOT = "https://jsoc1.stanford.edu/data/hmi/images/"
SDO_HMI_NAME_IC = "_Ic_4k.jpg"
SDO_HMI_NAME_IC_FLAT = "_Ic_flat_4k.jpg"
SDO_HMI_NAME_M = "_M_4k.jpg"
SDO_HMI_SNAME_M_COLOR = "_M_color_4k.jpg"

def fetch_hmi(output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    r = requests.get(SDO_HMI_LIVE_ROOT + "image_times.json")

    if r.status_code != 200:
        raise Exception("SDO server connection error: " + r.status_code)
    
    data = r.json()

    image_source = SDO_HMI_LIVE_ROOT + datetime.now().strftime("%Y/%m/%d") + "/" + data["last"] + SDO_HMI_NAME_M
    response = requests.get(image_source)
    response.raise_for_status()

    imager_path = output_dir / "hmi_m.jpg"
    with open(imager_path, "wb") as f:
        f.write(response.content)

    return {
        "hmi_m": imager_path.as_posix()
    }


DSCOVR_2H_PLASMA_URL = "https://services.swpc.noaa.gov/products/solar-wind/plasma-2-hour.json"
DSCOVR_2H_MAG_URL = "https://services.swpc.noaa.gov/products/solar-wind/mag-2-hour.json"

def fetch_sensors(output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)

    r = requests.get(DSCOVR_2H_MAG_URL)
    r.raise_for_status()
    data = r.json()

    mag_df = pd.DataFrame(data[1:], columns=data[0])
    mag_df["timestamp"] = pd.to_datetime(mag_df["time_tag"])
    mag_df["bx_gsm"] = pd.to_numeric(mag_df["bx_gsm"])
    mag_df["by_gsm"] = pd.to_numeric(mag_df["by_gsm"])
    mag_df["bz_gsm"] = pd.to_numeric(mag_df["bz_gsm"])
    mag_df["lon_gsm"] = pd.to_numeric(mag_df["lon_gsm"])
    mag_df["lat_gsm"] = pd.to_numeric(mag_df["lat_gsm"])
    mag_df["bt"] = pd.to_numeric(mag_df["bt"])

    mag_df = mag_df.set_index("timestamp")
    mag_df = mag_df.drop(["time_tag"], axis=1)
    

    imf_path = output_dir / "imf.csv"
    mag_df.to_csv(imf_path)

    r = requests.get(DSCOVR_2H_PLASMA_URL)
    r.raise_for_status()
    data = r.json()
    plasma_df = pd.DataFrame(data[1:], columns=data[0])
    plasma_df["timestamp"] = pd.to_datetime(plasma_df["time_tag"])
    plasma_df["density"] = pd.to_numeric(plasma_df["density"])
    plasma_df["speed"] = pd.to_numeric(plasma_df["speed"])
    plasma_df["temperature"] = pd.to_numeric(plasma_df["temperature"])

    plasma_df = plasma_df.set_index("timestamp")
    plasma_df = plasma_df.drop(["time_tag"], axis=1)
    

    plasma_path = output_dir / "plasma.csv"
    plasma_df.to_csv(plasma_path)

    return {
        "imf_path": imf_path.as_posix(),
        "plasma_path": plasma_path.as_posix(),
        "Bx": mag_df.iloc[-1]["bx_gsm"].item(),
        "By": mag_df.iloc[-1]["by_gsm"].item(),
        "Bz": mag_df.iloc[-1]["bz_gsm"].item(),
        "V": plasma_df.iloc[-1]["speed"].item(),
        "N": plasma_df.iloc[-1]["density"].item(),
        "T": plasma_df.iloc[-1]["temperature"].item(),
    }


def fetch_all(output_dir: Path):
    return {
        "timestamp": datetime.now().isoformat(),
        "sensors": fetch_sensors(output_dir),
        "aia": fetch_aia(output_dir),
        "hmi": fetch_hmi(output_dir)
    }
