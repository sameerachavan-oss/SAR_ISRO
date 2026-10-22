
from pathlib import Path
import math

import numpy as np
import rasterio
from PIL import Image, ImageDraw, ImageFont


# --------------------------------------------------
# PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent
PATCH_DIR = PROJECT_DIR / "patches"
SAR_PREVIEW_DIR = PROJECT_DIR / "previews" / "sar"
OUTPUT_DIR = PROJECT_DIR / "previews"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Contact sheet layout
PATCHES_PER_SHEET = 12
COLUMNS = 3

# Each patch pair gets one panel.
PANEL_WIDTH = 440
IMAGE_SIZE = 190
HEADER_HEIGHT = 42
GAP = 16
BOTTOM_LABEL_HEIGHT = 30


# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def get_font(size=18):
    """Load a common Windows font, with a fallback."""
    candidates = [
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ]

    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)

    return ImageFont.load_default()


def optical_to_rgb(tif_path):
    """Create a display RGB image from an optical GeoTIFF."""

    with rasterio.open(tif_path) as src:
        if src.count < 3:
            raise ValueError(
                f"{tif_path.name} has fewer than 3 bands."
            )

        bands = [
            src.read(i, masked=True).filled(np.nan).astype(np.float32)
            for i in (1, 2, 3)
        ]

    rgb_bands = []

    for band in bands:
        valid = np.isfinite(band)

        if not valid.any():
            rgb_bands.append(
                np.zeros(band.shape, dtype=np.uint8)
            )
            continue

        low, high = np.percentile(band[valid], [2, 98])

        if high <= low:
            rgb_bands.append(
                np.zeros(band.shape, dtype=np.uint8)
            )
            continue

        scaled = np.zeros(band.shape, dtype=np.float32)
        scaled[valid] = (
            (band[valid] - low) / (high - low)
        )
        scaled = np.clip(scaled, 0, 1)

        rgb_bands.append(
            np.round(scaled * 255).astype(np.uint8)
        )

    rgb = np.stack(rgb_bands, axis=-1)
    return Image.fromarray(rgb)


def fit_image(image, size):
    """Resize an image to fit a square without distortion."""
    image = image.copy()
    image.thumbnail((size, size))
    canvas = Image.new("RGB", (size, size), "black")
    x = (size - image.width) // 2
    y = (size - image.height) // 2
    canvas.paste(image, (x, y))
    return canvas


# --------------------------------------------------
# CONTACT SHEET
# --------------------------------------------------

def create_contact_sheet(city, optical_folder, sar_folder, output_file):
    optical_folder = PROJECT_DIR / optical_folder
    sar_folder = PROJECT_DIR / sar_folder

    optical_files = sorted(optical_folder.glob("*.tif"))

    pairs = []

    for optical_path in optical_files:
        # Example: GOA_000001_OPT.tif -> GOA_000001
        patch_id = optical_path.stem.replace("_OPT", "")
        sar_path = sar_folder / f"{patch_id}_SAR.tif"
        preview_path = SAR_PREVIEW_DIR / f"{patch_id}_SAR.png"

        if sar_path.exists() and preview_path.exists():
            pairs.append(
                (patch_id, optical_path, sar_path, preview_path)
            )

    if not pairs:
        print(f"No matching image pairs found for {city}.")
        print(f"Checked optical folder: {optical_folder}")
        print(f"Checked SAR folder: {sar_folder}")
        return

    font = get_font(16)
    title_font = get_font(22)

    total_sheets = math.ceil(len(pairs) / PATCHES_PER_SHEET)

    for sheet_number in range(total_sheets):
        start = sheet_number * PATCHES_PER_SHEET
        sheet_pairs = pairs[start:start + PATCHES_PER_SHEET]

        rows = math.ceil(len(sheet_pairs) / COLUMNS)
        panel_height = (
            HEADER_HEIGHT
            + IMAGE_SIZE
            + BOTTOM_LABEL_HEIGHT
        )

        sheet_width = (
            COLUMNS * PANEL_WIDTH
            + (COLUMNS + 1) * GAP
        )
        sheet_height = (
            rows * panel_height
            + (rows + 1) * GAP
            + 48
        )

        sheet = Image.new(
            "RGB",
            (sheet_width, sheet_height),
            (245, 245, 245),
        )
        draw = ImageDraw.Draw(sheet)

        draw.text(
            (GAP, 10),
            f"{city} optical and SAR patches "
            f"- sheet {sheet_number + 1}/{total_sheets}",
            fill="black",
            font=title_font,
        )

        for index, pair in enumerate(sheet_pairs):
            patch_id, optical_path, sar_path, preview_path = pair

            row = index // COLUMNS
            col = index % COLUMNS

            x = GAP + col * (PANEL_WIDTH + GAP)
            y = 48 + GAP + row * (panel_height + GAP)

            draw.text(
                (x, y),
                patch_id,
                fill="black",
                font=font,
            )

            optical = fit_image(
                optical_to_rgb(optical_path),
                IMAGE_SIZE,
            )

            with Image.open(preview_path) as opened:
                sar_preview = fit_image(
                    opened.convert("RGB"),
                    IMAGE_SIZE,
                )

            image_y = y + HEADER_HEIGHT

            draw.text(
                (x, image_y - 22),
                "Optical",
                fill="black",
                font=font,
            )

            draw.text(
                (x + IMAGE_SIZE + 24, image_y - 22),
                "SAR preview",
                fill="black",
                font=font,
            )

            sheet.paste(optical, (x, image_y))
            sheet.paste(
                sar_preview,
                (x + IMAGE_SIZE + 24, image_y),
            )

        sheet_path = output_file.with_name(
            f"{output_file.stem}_{sheet_number + 1:02d}.png"
        )

        sheet.save(sheet_path)

        print(f"Saved: {sheet_path}")

    print(f"{city}: {len(pairs)} matching pairs reviewed in contact sheets.")


# --------------------------------------------------
# RUN FOR GOA AND MUMBAI
# --------------------------------------------------

def main():
    create_contact_sheet(
        city="Goa",
        optical_folder="patches/optical",
        sar_folder="patches/sar",
        output_file=OUTPUT_DIR / "contact_sheet_goa.png",
    )

    create_contact_sheet(
        city="Mumbai",
        optical_folder="patches/mumbai/optical",
        sar_folder="patches/mumbai/sar",
        output_file=OUTPUT_DIR / "contact_sheet_mumbai.png",
    )


if __name__ == "__main__":
    main()
