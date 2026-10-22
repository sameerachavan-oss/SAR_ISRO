
import csv
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.windows import bounds as window_bounds

# Project folder
BASE = Path(__file__).resolve().parent.parent

# Original Mumbai images
SAR_FILE = BASE / "original_geotiff" / "Mumbai_Coastal_SAR_VV_VH.tif"
OPTICAL_FILE = BASE / "original_geotiff" / "Mumbai_Coastal_Optical_RGB.tif"

# Mumbai-only output folders
SAR_OUT = BASE / "patches" / "mumbai" / "sar"
OPTICAL_OUT = BASE / "patches" / "mumbai" / "optical"
CSV_OUT = BASE / "metadata" / "mumbai_patch_inventory.csv"

PATCH_SIZE = 256
STRIDE = 128


def main():
    SAR_OUT.mkdir(parents=True, exist_ok=True)
    OPTICAL_OUT.mkdir(parents=True, exist_ok=True)
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)

    if not SAR_FILE.exists() or not OPTICAL_FILE.exists():
        raise FileNotFoundError(
            "Mumbai SAR or optical GeoTIFF was not found in original_geotiff."
        )

    records = []

    with rasterio.open(SAR_FILE) as sar, rasterio.open(OPTICAL_FILE) as optical:
        print("Checking Mumbai source images...")
        print(f"SAR CRS: {sar.crs}")
        print(f"Optical CRS: {optical.crs}")
        print(f"SAR dimensions: {sar.width} x {sar.height}")
        print(f"Optical dimensions: {optical.width} x {optical.height}")
        print(f"SAR bands: {sar.count}")
        print(f"Optical bands: {optical.count}")

        # Matching grids are essential for correctly paired patches.
        if sar.crs != optical.crs:
            raise ValueError("CRS mismatch: SAR and optical images differ.")

        if sar.width != optical.width or sar.height != optical.height:
            raise ValueError(
                "Dimension mismatch: SAR and optical images differ."
            )

        if not sar.transform.almost_equals(optical.transform):
            raise ValueError(
                "Grid mismatch: SAR and optical geotransforms differ."
            )

        if sar.width < PATCH_SIZE or sar.height < PATCH_SIZE:
            raise ValueError("The image is smaller than the requested patch size.")

        print("\nGrid matches. Extracting patches...")
        patch_number = 0
        skipped = 0

        for row in range(0, sar.height - PATCH_SIZE + 1, STRIDE):
            for col in range(0, sar.width - PATCH_SIZE + 1, STRIDE):
                window = Window(col, row, PATCH_SIZE, PATCH_SIZE)

                sar_data = sar.read(window=window)
                optical_data = optical.read(window=window)

                # Require every band and every pixel to be valid in both images.
                sar_valid = np.all(sar.read_masks(window=window) > 0, axis=0)
                optical_valid = np.all(
                    optical.read_masks(window=window) > 0, axis=0
                )

                if not sar_valid.all() or not optical_valid.all():
                    skipped += 1
                    continue

                patch_number += 1
                patch_id = f"MUMBAI_{patch_number:06d}"

                sar_path = SAR_OUT / f"{patch_id}_SAR.tif"
                optical_path = OPTICAL_OUT / f"{patch_id}_OPT.tif"

                sar_profile = sar.profile.copy()
                sar_profile.update(
                    width=PATCH_SIZE,
                    height=PATCH_SIZE,
                    transform=rasterio.windows.transform(window, sar.transform),
                )

                optical_profile = optical.profile.copy()
                optical_profile.update(
                    width=PATCH_SIZE,
                    height=PATCH_SIZE,
                    transform=rasterio.windows.transform(
                        window, optical.transform
                    ),
                )

                with rasterio.open(sar_path, "w", **sar_profile) as dst:
                    dst.write(sar_data)

                with rasterio.open(
                    optical_path, "w", **optical_profile
                ) as dst:
                    dst.write(optical_data)

                left, bottom, right, top = window_bounds(window, sar.transform)

                records.append({
                    "city": "Mumbai",
                    "patch_id": patch_id,
                    "row_start": row,
                    "col_start": col,
                    "patch_size": PATCH_SIZE,
                    "stride": STRIDE,
                    "crs": str(sar.crs),
                    "left": left,
                    "bottom": bottom,
                    "right": right,
                    "top": top,
                    "sar_path": str(sar_path.relative_to(BASE)),
                    "optical_path": str(optical_path.relative_to(BASE)),
                    "caption": "",
                    "split": "",
                })

    fieldnames = [
        "city", "patch_id", "row_start", "col_start",
        "patch_size", "stride", "crs",
        "left", "bottom", "right", "top",
        "sar_path", "optical_path", "caption", "split",
    ]

    with open(CSV_OUT, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print("\nMumbai patch extraction finished!")
    print(f"Saved matching patch pairs: {len(records)}")
    print(f"Skipped pairs with invalid pixels: {skipped}")
    print(f"SAR patches: {SAR_OUT}")
    print(f"Optical patches: {OPTICAL_OUT}")
    print(f"CSV inventory: {CSV_OUT}")


if __name__ == "__main__":
    main()

