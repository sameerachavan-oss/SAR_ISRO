
import pandas as pd
from pathlib import Path

csv_path = Path("metadata/caption_dataset_master.csv")
df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)

print("Total records:", len(df))
print("Total columns:", len(df.columns))
print("Non-empty verified captions:",
      df["caption_verified"].str.strip().ne("").sum())

print("\nCaptions by city:")
print(
    df.assign(
        has_caption=df["caption_verified"].str.strip().ne("")
    )
    .groupby("city")["has_caption"]
    .sum()
)

print("\nGoa caption status:")
for start, end in [(1, 55), (56, 110)]:
    ids = [f"GOA_{i:06d}" for i in range(start, end + 1)]
    subset = df[df["patch_id"].isin(ids)]
    count = subset["caption_verified"].str.strip().ne("").sum()
    print(f"GOA_{start:06d}–GOA_{end:06d}: {count}/{len(ids)}")

print("\nVerification status counts:")
print(df["verification_status"].value_counts().to_string())
