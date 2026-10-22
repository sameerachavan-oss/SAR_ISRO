
from pathlib import Path
from datetime import datetime

import pandas as pd
import rasterio
import numpy as np


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

CSV = Path("metadata/caption_dataset_master.csv")

BLOCK_SIZE_METERS = 10000  # 10 km spatial blocks
VALIDATION_RATIO = 0.20
RANDOM_SEED = 42


# --------------------------------------------------
# 2. LOAD DATASET
# --------------------------------------------------

if not CSV.exists():
    raise FileNotFoundError(
        f"Dataset CSV not found: {CSV.resolve()}"
    )

df = pd.read_csv(
    CSV,
    dtype=str,
    keep_default_na=False
)

required_columns = {
    "patch_id",
    "city",
    "sar_path",
    "caption_verified",
    "split",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing columns in CSV: {missing_columns}"
    )

if df.empty:
    raise ValueError("The dataset CSV is empty.")

if df["patch_id"].duplicated().any():
    duplicates = df.loc[
        df["patch_id"].duplicated(),
        "patch_id"
    ].tolist()

    raise ValueError(
        f"Duplicate patch IDs found: {duplicates[:10]}"
    )

if df["caption_verified"].str.strip().eq("").any():
    missing_count = int(
        df["caption_verified"].str.strip().eq("").sum()
    )

    raise ValueError(
        f"{missing_count} patches have missing verified captions."
    )

print(f"Total patches: {len(df)}")
print("\nPatches by city:")
print(df["city"].value_counts())


# --------------------------------------------------
# 3. READ GEOTIFF SPATIAL BOUNDS
# --------------------------------------------------

bounds = []
projected_crs = {}

for _, row in df.iterrows():

    sar_path = Path(row["sar_path"])

    # Paths are expected to be relative to the project root.
    if not sar_path.exists():
        sar_path = CSV.parent.parent / row["sar_path"]

    if not sar_path.exists():
        raise FileNotFoundError(
            f"SAR image not found for {row['patch_id']}: "
            f"{sar_path.resolve()}"
        )

    with rasterio.open(sar_path) as src:

        if src.crs is None:
            raise ValueError(
                f"Missing CRS in image: {sar_path}"
            )

        if not src.crs.is_projected:
            raise ValueError(
                f"Image CRS is not projected: "
                f"{sar_path} ({src.crs})"
            )

        # The script assumes projected coordinates measured in metres.
        unit_factor = src.crs.linear_units_factor

        if isinstance(unit_factor, tuple):
            unit_factor = unit_factor[1]

        if not np.isclose(unit_factor, 1.0):
            raise ValueError(
                f"CRS coordinates are not in metres: "
                f"{sar_path} ({src.crs})"
            )

        crs_name = src.crs.to_string()

        # Record CRS per city to catch inconsistent coordinate systems.
        city = row["city"]
        if city in projected_crs:
            if projected_crs[city] != crs_name:
                raise ValueError(
                    f"Inconsistent CRS for {city}: "
                    f"{projected_crs[city]} and {crs_name}"
                )
        else:
            projected_crs[city] = crs_name

        b = src.bounds

        bounds.append(
            (b.left, b.bottom, b.right, b.top)
        )

df[["left", "bottom", "right", "top"]] = pd.DataFrame(
    bounds,
    index=df.index
)

print("\nCRS by city:")
for city, crs_name in projected_crs.items():
    print(f"{city}: {crs_name}")


# --------------------------------------------------
# 4. CREATE SPATIAL GROUPS
# --------------------------------------------------

# Each patch is assigned to a 10 km grid block based
# on its lower-left coordinate.
df["block_x"] = np.floor(
    df["left"] / BLOCK_SIZE_METERS
).astype(int)

df["block_y"] = np.floor(
    df["bottom"] / BLOCK_SIZE_METERS
).astype(int)

df["spatial_group"] = (
    df["city"].astype(str)
    + "_"
    + df["block_x"].astype(str)
    + "_"
    + df["block_y"].astype(str)
)


# --------------------------------------------------
# 5. SPLIT SPATIAL GROUPS INTO TRAIN AND VALIDATION
# --------------------------------------------------

rng = np.random.default_rng(RANDOM_SEED)

df["split"] = ""

for city, city_df in df.groupby("city"):

    # Convert to a NumPy array before shuffling.
    groups = np.array(
        city_df["spatial_group"].unique(),
        dtype=str
    )

    if len(groups) < 2:
        raise ValueError(
            f"{city} has only {len(groups)} spatial group(s). "
            "At least two groups are needed for a spatial split."
        )

    rng.shuffle(groups)

    n_val_groups = max(
        1,
        round(len(groups) * VALIDATION_RATIO)
    )

    # Keep at least one group in training.
    n_val_groups = min(
        n_val_groups,
        len(groups) - 1
    )

    val_groups = set(groups[:n_val_groups])

    city_mask = df["city"].eq(city)

    df.loc[city_mask, "split"] = (
        df.loc[city_mask, "spatial_group"]
        .apply(
            lambda group:
                "val" if group in val_groups else "train"
        )
    )


# --------------------------------------------------
# 6. REMOVE TEMPORARY COLUMNS
# --------------------------------------------------

temporary_columns = [
    "left",
    "bottom",
    "right",
    "top",
    "block_x",
    "block_y",
    "spatial_group",
]

df.drop(
    columns=temporary_columns,
    inplace=True
)


# --------------------------------------------------
# 7. VALIDATE THE SPLIT
# --------------------------------------------------

if df["split"].eq("").any():
    raise ValueError(
        "Some patches were not assigned a split."
    )

if not set(df["split"].unique()).issubset({"train", "val"}):
    raise ValueError(
        "Unexpected split values found."
    )

print("\nSplit counts:")
print(df["split"].value_counts())

print("\nSplit by city:")
print(pd.crosstab(df["city"], df["split"]))

print("\nSplit percentages:")
print(
    (df["split"].value_counts(normalize=True) * 100)
    .round(2)
    .astype(str)
    + "%"
)


# --------------------------------------------------
# 8. CREATE BACKUP WITHOUT OVERWRITING OLD BACKUPS
# --------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup = CSV.with_name(
    f"caption_dataset_master_before_split_{timestamp}.csv"
)

# Avoid overwriting a backup if the script is run
# more than once within the same second.
counter = 1

while backup.exists():
    backup = CSV.with_name(
        f"caption_dataset_master_before_split_"
        f"{timestamp}_{counter}.csv"
    )
    counter += 1

# Save the original CSV before updating it.
original_df = pd.read_csv(
    CSV,
    dtype=str,
    keep_default_na=False
)

original_df.to_csv(
    backup,
    index=False,
    encoding="utf-8-sig"
)


# --------------------------------------------------
# 9. SAVE UPDATED MASTER CSV
# --------------------------------------------------

df.to_csv(
    CSV,
    index=False,
    encoding="utf-8-sig"
)

print("\nSUCCESS: Train/validation split created.")
print(f"Total patches: {len(df)}")
print(f"Training patches: {(df['split'] == 'train').sum()}")
print(f"Validation patches: {(df['split'] == 'val').sum()}")
print(f"Backup saved: {backup}")
print(f"Updated dataset: {CSV}")
