
from pathlib import Path
import csv

import numpy as np
import rasterio
from rasterio.windows import Window
from rasterio.transform import array_bounds


# =========================================================
# 1. PROJECT SETTINGS
# =========================================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

SAR_FILE = (
    PROJECT_DIR
    / "original_geotiff"
    / "Goa_Coastal_SAR_VV_VH.tif"
)

OPTICAL_FILE = (
    PROJECT_DIR
    / "original_geotiff"
    / "Goa_Coastal_Optical_RGB.tif"
)

SAR_OUT = PROJECT_DIR / "patches" / "sar"
OPTICAL_OUT = PROJECT_DIR / "patches" / "optical"

CSV_FILE = PROJECT_DIR / "metadata" / "goa_patch_inventory.csv"

# Patch configuration
PATCH_SIZE = 256
STRIDE = 128  # 50% overlap


# =========================================================
# 2. MAIN FUNCTION
# =========================================================

def main():

    # Create output folders
    SAR_OUT.mkdir(parents=True, exist_ok=True)
    OPTICAL_OUT.mkdir(parents=True, exist_ok=True)
    CSV_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Check input files
    if not SAR_FILE.exists():
        raise FileNotFoundError(f"SAR file not found:\n{SAR_FILE}")

    if not OPTICAL_FILE.exists():
        raise FileNotFoundError(
            f"Optical file not found:\n{OPTICAL_FILE}"
        )

    rows = []
    skipped_count = 0
    saved_count = 0

    # Open both source GeoTIFFs
    with rasterio.open(SAR_FILE) as sar, \
            rasterio.open(OPTICAL_FILE) as optical:

        # -------------------------------------------------
        # 3. CHECK IMAGE ALIGNMENT
        # -------------------------------------------------

        print("\nChecking source images...")

        if sar.crs != optical.crs:
            raise ValueError(
                f"CRS mismatch!\n"
                f"SAR CRS: {sar.crs}\n"
                f"Optical CRS: {optical.crs}"
            )

        if sar.width != optical.width or \
                sar.height != optical.height:
            raise ValueError(
                "Image dimensions do not match. "
                "Align the images before extracting patches."
            )

        if sar.transform != optical.transform:
            raise ValueError(
                "Geographic transforms do not match. "
                "Align the images before extracting patches."
            )

        if sar.width < PATCH_SIZE or sar.height < PATCH_SIZE:
            raise ValueError(
                "Source image is smaller than the requested patch size."
            )

        print("Alignment checks passed.")
        print(f"CRS: {sar.crs}")
        print(f"Image dimensions: {sar.width} x {sar.height}")
        print(f"SAR band count: {sar.count}")
        print(f"Optical band count: {optical.count}")
        print(f"Patch size: {PATCH_SIZE} x {PATCH_SIZE}")
        print(f"Stride: {STRIDE}")

        # Calculate expected number of windows
        columns = (sar.width - PATCH_SIZE) // STRIDE + 1
        row_count = (sar.height - PATCH_SIZE) // STRIDE + 1
        possible_count = columns * row_count

        print(f"Possible paired patches: {possible_count}")
        print("\nExtracting patches...")

        # -------------------------------------------------
        # 4. EXTRACT MATCHING PATCHES
        # -------------------------------------------------

        for row_start in range(
            0, sar.height - PATCH_SIZE + 1, STRIDE
        ):

            for col_start in range(
                0, sar.width - PATCH_SIZE + 1, STRIDE
            ):

                window = Window(
                    col_off=col_start,
                    row_off=row_start,
                    width=PATCH_SIZE,
                    height=PATCH_SIZE,
                )

                # Read all bands without changing pixel values
                sar_data = sar.read(window=window)
                optical_data = optical.read(window=window)

                # Read validity masks for all bands
                sar_masks = sar.read_masks(window=window)
                optical_masks = optical.read_masks(window=window)

                # A pixel is valid only if all its bands are valid
                sar_valid = np.all(sar_masks > 0, axis=0)
                optical_valid = np.all(optical_masks > 0, axis=0)

                # Skip the pair if either image has invalid pixels
                if not np.all(sar_valid) or \
                        not np.all(optical_valid):
                    skipped_count += 1
                    continue

                # Assign the next sequential ID to valid pairs
                saved_count += 1
                patch_id = f"GOA_{saved_count:06d}"

                sar_path = SAR_OUT / f"{patch_id}_SAR.tif"
                optical_path = OPTICAL_OUT / f"{patch_id}_OPT.tif"

                # Geographic transform for this patch
                patch_transform = sar.window_transform(window)

                # Preserve source metadata and update patch dimensions
                sar_profile = sar.profile.copy()
                sar_profile.update(
                    driver="GTiff",
                    width=PATCH_SIZE,
                    height=PATCH_SIZE,
                    transform=patch_transform,
                    compress="LZW",
                    BIGTIFF="IF_SAFER",
                )

                optical_profile = optical.profile.copy()
                optical_profile.update(
                    driver="GTiff",
                    width=PATCH_SIZE,
                    height=PATCH_SIZE,
                    transform=patch_transform,
                    compress="LZW",
                    BIGTIFF="IF_SAFER",
                )

                # Write SAR patch
                with rasterio.open(
                    sar_path, "w", **sar_profile
                ) as dst:
                    dst.write(sar_data)

                # Write corresponding optical patch
                with rasterio.open(
                    optical_path, "w", **optical_profile
                ) as dst:
                    dst.write(optical_data)

                # Calculate geographic bounds
                west, south, east, north = array_bounds(
                    PATCH_SIZE,
                    PATCH_SIZE,
                    patch_transform,
                )

                # Save patch metadata
                rows.append({
                    "patch_id": patch_id,
                    "region": "Goa_coastal",
                    "row_start": row_start,
                    "col_start": col_start,
                    "patch_size_pixels": PATCH_SIZE,
                    "stride_pixels": STRIDE,
                    "crs": str(sar.crs),
                    "west": west,
                    "south": south,
                    "east": east,
                    "north": north,
                    "sar_path": sar_path.relative_to(
                        PROJECT_DIR
                    ).as_posix(),
                    "optical_path": optical_path.relative_to(
                        PROJECT_DIR
                    ).as_posix(),
                    "caption": "",
                    "split": "",
                })

                if saved_count % 10 == 0:
                    print(
                        f"Saved {saved_count} paired patches..."
                    )

    # -------------------------------------------------
    # 5. SAVE CSV INVENTORY
    # -------------------------------------------------

    fieldnames = [
        "patch_id",
        "region",
        "row_start",
        "col_start",
        "patch_size_pixels",
        "stride_pixels",
        "crs",
        "west",
        "south",
        "east",
        "north",
        "sar_path",
        "optical_path",
        "caption",
        "split",
    ]

    with open(
        CSV_FILE,
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)

    # -------------------------------------------------
    # 6. PRINT SUMMARY
    # -------------------------------------------------

    print("\n========================================")
    print("PATCH EXTRACTION COMPLETED")
    print("========================================")

    print(f"Patch dimensions: {PATCH_SIZE} x {PATCH_SIZE}")
    print(f"Stride: {STRIDE} pixels")
    print(f"Possible windows: {possible_count}")
    print(f"Saved paired patches: {saved_count}")
    print(f"Skipped windows: {skipped_count}")

    print(f"\nSAR patches folder:\n{SAR_OUT}")
    print(f"\nOptical patches folder:\n{OPTICAL_OUT}")
    print(f"\nCSV inventory:\n{CSV_FILE}")

    print("\nOriginal GeoTIFFs were not modified.")
    print("========================================")


# =========================================================
# 7. RUN SCRIPT
# =========================================================

if __name__ == "__main__":
    main()
