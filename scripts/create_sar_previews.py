
from pathlib import Path
import warnings

import numpy as np
import rasterio
from PIL import Image


# --------------------------------------------------
# 1. PROJECT FOLDERS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

SAR_PATCH_FOLDERS = [
    PROJECT_DIR / "patches" / "sar",
    PROJECT_DIR / "patches" / "mumbai" / "sar",
]

PREVIEW_DIR = PROJECT_DIR / "previews" / "sar"

PREVIEW_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. SAR DISPLAY SETTINGS
# --------------------------------------------------
# These limits are used ONLY to make preview PNGs.
# They do not modify the original SAR GeoTIFF files.
#
# Band 1 = VV
# Band 2 = VH
#
# Confirm the source data units before using these
# limits for scientific analysis or model training.

VV_LOW = -30.0
VV_HIGH = 5.0

VH_LOW = -40.0
VH_HIGH = 0.0


# --------------------------------------------------
# 3. CONVERT SAR VALUES TO 8-BIT DISPLAY VALUES
# --------------------------------------------------

def scale_band(band, low, high):
    """Scale valid SAR values to uint8 safely."""

    band = np.asarray(band, dtype=np.float32)

    # Identify valid numbers and ignore NaN/infinity.
    valid = np.isfinite(band)

    # Start with zeros so invalid pixels stay black.
    scaled = np.zeros(band.shape, dtype=np.float32)

    if high <= low:
        raise ValueError(
            f"Invalid display limits: low={low}, high={high}"
        )

    # Scale only valid pixels.
    scaled[valid] = (
        (band[valid] - low) / (high - low)
    )

    # Keep values in the display range.
    scaled = np.clip(scaled, 0.0, 1.0)

    # Convert safely to 8-bit image values.
    return np.round(scaled * 255).astype(np.uint8)


# --------------------------------------------------
# 4. CREATE A FALSE-COLOR SAR PREVIEW
# --------------------------------------------------

def create_preview(input_file, output_file):
    """Read a two-band SAR GeoTIFF and save a PNG preview."""

    with rasterio.open(input_file) as src:

        if src.count < 2:
            print(
                f"SKIPPED: {input_file.name} "
                f"has only {src.count} band(s); expected VV and VH."
            )
            return False

        # Read the first two bands.
        # Expected: band 1 = VV, band 2 = VH.
        vv = src.read(1, masked=True).filled(np.nan)
        vh = src.read(2, masked=True).filled(np.nan)

        # Convert each band to an 8-bit display image.
        vv_display = scale_band(vv, VV_LOW, VV_HIGH)
        vh_display = scale_band(vh, VH_LOW, VH_HIGH)

        # False-color display:
        # Red   = VV
        # Green = VH
        # Blue  = VH
        #
        # This is a visualization, NOT optical RGB.
        rgb = np.stack(
            [vv_display, vh_display, vh_display],
            axis=-1,
        )

        # Save only the preview PNG.
        # The original GeoTIFF remains unchanged.
        Image.fromarray(rgb, mode="RGB").save(output_file)

    return True


# --------------------------------------------------
# 5. PROCESS ALL SAR PATCHES
# --------------------------------------------------

def main():
    total_processed = 0
    total_skipped = 0

    print("=" * 60)
    print("SAR PREVIEW GENERATION")
    print("=" * 60)

    for sar_folder in SAR_PATCH_FOLDERS:

        if not sar_folder.exists():
            print(f"Folder not found; skipping: {sar_folder}")
            continue

        sar_files = sorted(sar_folder.glob("*.tif"))

        print(f"\nInput folder: {sar_folder}")
        print(f"SAR GeoTIFF files found: {len(sar_files)}")

        for input_file in sar_files:

            output_file = PREVIEW_DIR / (
                input_file.stem + ".png"
            )

            try:
                success = create_preview(
                    input_file,
                    output_file,
                )

                if success:
                    total_processed += 1
                else:
                    total_skipped += 1

            except Exception as error:
                total_skipped += 1
                print(f"ERROR processing {input_file.name}: {error}")

    print("\n" + "=" * 60)
    print("PREVIEW GENERATION COMPLETE")
    print("=" * 60)
    print(f"Files processed successfully: {total_processed}")
    print(f"Files skipped or failed: {total_skipped}")
    print(f"Preview folder: {PREVIEW_DIR}")


if __name__ == "__main__":
    main()


