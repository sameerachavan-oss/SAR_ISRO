
import csv
from pathlib import Path

import rasterio

BASE = Path(__file__).resolve().parent.parent
OUTPUT = BASE / "metadata" / "caption_dataset_master.csv"

# City name, SAR folder, optical folder, filename prefix
DATASETS = [
    (
        "Goa",
        BASE / "patches" / "sar",
        BASE / "patches" / "optical",
        "GOA",
    ),
    (
        "Mumbai",
        BASE / "patches" / "mumbai" / "sar",
        BASE / "patches" / "mumbai" / "optical",
        "MUMBAI",
    ),
]

FIELDS = [
    "patch_id",
    "city",
    "sar_path",
    "optical_path",
    "width",
    "height",
    "sar_bands",
    "optical_bands",
    "crs",
    "caption_draft",
    "caption_verified",
    "verification_status",
    "reviewer_notes",
    "split",
]


def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    errors = []

    for city, sar_dir, optical_dir, prefix in DATASETS:
        if not sar_dir.exists() or not optical_dir.exists():
            raise FileNotFoundError(
                f"Missing patch folder for {city}: "
                f"{sar_dir} or {optical_dir}"
            )

        sar_files = sorted(sar_dir.glob(f"{prefix}_*_SAR.tif"))

        for sar_path in sar_files:
            patch_id = sar_path.name.removesuffix("_SAR.tif")
            optical_path = optical_dir / f"{patch_id}_OPT.tif"

            if not optical_path.exists():
                errors.append(f"Missing optical pair: {optical_path}")
                continue

            with rasterio.open(sar_path) as sar, \
                 rasterio.open(optical_path) as optical:

                # Check that the paired patches have matching grids.
                if (
                    sar.crs != optical.crs
                    or sar.width != optical.width
                    or sar.height != optical.height
                    or not sar.transform.almost_equals(optical.transform)
                ):
                    errors.append(f"Grid mismatch: {patch_id}")
                    continue

                rows.append({
                    "patch_id": patch_id,
                    "city": city,
                    "sar_path": sar_path.relative_to(BASE).as_posix(),
                    "optical_path": optical_path.relative_to(BASE).as_posix(),
                    "width": sar.width,
                    "height": sar.height,
                    "sar_bands": sar.count,
                    "optical_bands": optical.count,
                    "crs": str(sar.crs),
                    "caption_draft": "",
                    "caption_verified": "",
                    "verification_status": "pending",
                    "reviewer_notes": "",
                    "split": "",
                })

    rows.sort(key=lambda item: item["patch_id"])

    if errors:
        print("Problems found:")
        for error in errors:
            print(" -", error)

        raise RuntimeError(
            "Fix the missing pairs or grid mismatches before creating "
            "the final inventory."
        )

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print("\nInventory created successfully.")
    print(f"Total paired records: {len(rows)}")
    print(f"Goa records: {sum(r['city'] == 'Goa' for r in rows)}")
    print(f"Mumbai records: {sum(r['city'] == 'Mumbai' for r in rows)}")
    print(f"Output: {OUTPUT}")


if __name__ == "__main__":
    main()
