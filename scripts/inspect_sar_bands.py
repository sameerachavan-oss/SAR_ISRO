

from pathlib import Path

import numpy as np
import rasterio

# Project directory: SAR_ISRO
BASE = Path(__file__).resolve().parent.parent

# Original SAR GeoTIFF files
FILES = [
    BASE / "original_geotiff" / "Goa_Coastal_SAR_VV_VH.tif",
    BASE / "original_geotiff" / "Mumbai_Coastal_SAR_VV_VH.tif",
]


def inspect_sar_file(path):
    print("\n" + "=" * 70)
    print(f"FILE: {path.name}")
    print("=" * 70)

    if not path.exists():
        print(f"ERROR: File not found: {path}")
        return

    with rasterio.open(path) as src:
        print(f"CRS: {src.crs}")
        print(f"Dimensions: {src.width} x {src.height}")
        print(f"Number of bands: {src.count}")
        print(f"Data types: {src.dtypes}")
        print(f"Band descriptions: {src.descriptions}")
        print(f"Band units: {src.units}")
        print(f"NoData values: {src.nodatavals}")
        print(f"Pixel size: {src.res}")

        for band in range(1, src.count + 1):
            print(f"\n--- BAND {band} ---")

            # Read the band while excluding masked/no-data pixels
            data = src.read(band, masked=True)
            values = data.compressed()

            if values.size == 0:
                print("No valid pixels found.")
                continue

            # Ignore any remaining non-finite values
            values = values[np.isfinite(values)]

            if values.size == 0:
                print("No finite pixel values found.")
                continue

            percentiles = np.percentile(
                values, [2, 25, 50, 75, 98]
            )

            print(f"Valid pixel count: {values.size:,}")
            print(f"Minimum: {values.min():.6f}")
            print(f"Maximum: {values.max():.6f}")
            print(f"Mean: {values.mean():.6f}")
            print(f"Median: {np.median(values):.6f}")
            print(f"2nd percentile: {percentiles[0]:.6f}")
            print(f"25th percentile: {percentiles[1]:.6f}")
            print(f"50th percentile: {percentiles[2]:.6f}")
            print(f"75th percentile: {percentiles[3]:.6f}")
            print(f"98th percentile: {percentiles[4]:.6f}")

        print("\nAdditional metadata:")
        print(f"Driver: {src.driver}")
        print(f"Compression: {src.profile.get('compress')}")
        print(f"Transform: {src.transform}")


def main():
    for file_path in FILES:
        inspect_sar_file(file_path)

    print("\n" + "=" * 70)
    print("SAR BAND INSPECTION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()
