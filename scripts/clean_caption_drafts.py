
from pathlib import Path
from datetime import datetime
import pandas as pd
import sys

# ============================================================
# SAR_ISRO: SAFE CAPTION DRAFT CLEANUP
# Script location: SAR_ISRO/scripts/clean_caption_drafts.py
# Master CSV: SAR_ISRO/metadata/caption_dataset_master.csv
# ============================================================

# Resolve the project directory correctly
PROJECT_DIR = Path(__file__).resolve().parent.parent
METADATA_DIR = PROJECT_DIR / "metadata"

CSV_PATH = METADATA_DIR / "caption_dataset_master.csv"


def main():
    print("=" * 60)
    print("SAR_ISRO CAPTION DRAFT CLEANUP")
    print("=" * 60)

    # 1. Check that the master CSV exists
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Master CSV not found:\n{CSV_PATH}"
        )

    print(f"\nMaster CSV: {CSV_PATH}")

    # 2. Read the dataset
    df = pd.read_csv(CSV_PATH)

    print(f"Records found: {len(df)}")

    # 3. Validate the required columns
    required_columns = [
        "patch_id",
        "caption_draft",
        "caption_verified",
        "verification_status",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # 4. Validate record count and unique image IDs
    if len(df) != 220:
        raise ValueError(
            f"Expected 220 records, but found {len(df)}. "
            "No changes were made."
        )

    if df["patch_id"].isna().any():
        raise ValueError(
            "Some patch IDs are missing. No changes were made."
        )

    if df["patch_id"].duplicated().any():
        duplicates = df.loc[
            df["patch_id"].duplicated(keep=False), "patch_id"
        ].tolist()

        raise ValueError(
            f"Duplicate patch IDs found: {duplicates}. "
            "No changes were made."
        )

    print("Validation passed: 220 unique patch IDs.")

    # 5. Create a timestamped backup before editing
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_path = METADATA_DIR / (
        f"caption_dataset_master_before_cleanup_{timestamp}.csv"
    )

    # Copy the original file byte-for-byte
    backup_path.write_bytes(CSV_PATH.read_bytes())

    print(f"Backup created: {backup_path.name}")

    # 6. Count existing draft captions
    old_draft_count = int(
        df["caption_draft"].notna().sum()
    )

    # 7. Clear ONLY the old draft-caption column
    # All other columns remain unchanged.
    df["caption_draft"] = ""

    # 8. Save to a temporary file first
    temp_path = CSV_PATH.with_name(
        "caption_dataset_master.tmp"
    )

    try:
        df.to_csv(
            temp_path,
            index=False,
            encoding="utf-8-sig",
        )

        # 9. Verify the temporary CSV before replacing master
        check = pd.read_csv(temp_path)

        if len(check) != 220:
            raise ValueError(
                "Temporary CSV has an incorrect row count."
            )

        if check.columns.tolist() != df.columns.tolist():
            raise ValueError(
                "Column names changed unexpectedly."
            )

        if check["patch_id"].tolist() != df["patch_id"].tolist():
            raise ValueError(
                "Patch ID order changed unexpectedly."
            )

        if not check["caption_draft"].fillna("").eq("").all():
            raise ValueError(
                "Some old draft captions remain."
            )

        # Ensure the verified-caption values are preserved
        if not check["caption_verified"].equals(
            df["caption_verified"]
        ):
            raise ValueError(
                "Verified captions changed unexpectedly."
            )

        # 10. Replace master only after validation passes
        temp_path.replace(CSV_PATH)

    finally:
        # Remove leftover temporary file if one remains
        if temp_path.exists():
            temp_path.unlink()

    # 11. Final verification
    final_df = pd.read_csv(CSV_PATH)

    assert len(final_df) == 220
    assert final_df["patch_id"].is_unique
    assert final_df["caption_draft"].fillna("").eq("").all()

    print("\n" + "=" * 60)
    print("CLEANUP COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"Total records preserved: {len(final_df)}")
    print(f"Old draft captions cleared: {old_draft_count}")
    print(
        "Verified captions preserved:",
        int(final_df["caption_verified"].notna().sum()),
    )
    print(f"Total columns preserved: {len(final_df.columns)}")
    print(f"Backup file: {backup_path.name}")
    print("\nNo image IDs or records were intentionally removed.")
    print("Ready for the next caption-review step.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        sys.exit(1)
