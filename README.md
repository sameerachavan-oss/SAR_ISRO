<<<<<<< HEAD

@'
# SAR_ISRO: SAR Image Captioning Research
=======
﻿# SAR_ISRO: SAR Image Captioning Research
>>>>>>> 363deec (Add project README and Python requirements)

## Project Overview

This project explores vision-language approaches for semantic understanding and image captioning of Synthetic Aperture Radar (SAR) imagery.

The research is associated with the project topic:

**A Vision-Language Model for Prompt-Based Semantic Understanding of SAR Images**

The current prototype dataset focuses on coastal regions of Goa and Mumbai, India.

## Objectives

- Organize SAR imagery and corresponding optical imagery of the same locations.
- Extract spatially aligned image patches.
- Prepare a structured caption dataset with metadata.
- Review and improve captions for reliable semantic descriptions.
- Develop a foundation for future SAR image captioning and visual question answering (VQA) experiments.

## Current Dataset

The current dataset inventory contains:

- 4 original GeoTIFF files: SAR and optical imagery for Goa and Mumbai.
- 220 SAR image patches.
- 220 corresponding optical image patches.
- 220 records in the master caption CSV.
- Patch inventory CSV files for Goa and Mumbai.

The SAR imagery contains VV and VH polarization bands. The optical imagery contains RGB bands.

The original imagery is stored at 10 m pixel spacing, with the existing data recorded in CRS EPSG:32643. Verify the metadata of each source image before using it in further experiments.

**Caption status:** The presence of 220 dataset records does not mean all captions have been independently verified. Check the `caption_verified` and `verification_status` fields before using captions as ground truth.

## Project Structure

```text
SAR_ISRO/
├── README.md
├── requirements.txt
├── .gitignore
├── original_geotiff/
│   ├── Goa_Coastal_SAR_VV_VH.tif
│   ├── Goa_Coastal_Optical_RGB.tif
│   ├── Mumbai_Coastal_SAR_VV_VH.tif
│   └── Mumbai_Coastal_Optical_RGB.tif
├── patches/
│   ├── goa/
│   └── mumbai/
├── previews/
│   └── sar/
├── metadata/
│   ├── caption_dataset_master.csv
│   ├── goa_patch_inventory.csv
│   └── mumbai_patch_inventory.csv
├── scripts/
│   ├── extract_goa_patches.py
│   ├── extract_mumbai_patches.py
│   ├── create_sar_previews.py
│   ├── create_contact_sheets.py
│   ├── build_caption_inventory.py
│   ├── add_all_captions.py
│   ├── clean_caption_drafts.py
│   ├── check_caption_progress.py
│   ├── create_train_val_split.py
│   └── inspect_sar_bands.py
└── .venv/
```

The structure above is a guide. The actual contents of each folder may vary as the project develops. The virtual environment (`.venv/`) should be recreated on each computer rather than transferred.

## Software Requirements

- Python 3.11 or another version compatible with the installed geospatial libraries
- Rasterio
- NumPy
- Pandas
- Pillow
- Matplotlib

See `requirements.txt` for the initial package list. Add any additional dependencies required by individual scripts.

## Installation on Windows

### 1. Clone the repository

```powershell
git clone https://github.com/sameerachavan-oss/SAR_ISRO.git
cd SAR_ISRO
```

### 2. Create a virtual environment

```powershell
py -m venv .venv
```

### 3. Activate it

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use this for the current terminal session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 4. Install packages

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Obtain the dataset

The repository may not contain the original GeoTIFFs, extracted patches, or preview images. Obtain those files from the project's approved data storage and restore the expected folder structure before running extraction or preview scripts.

### 6. Run a script

For example, after restoring the required data:

```powershell
python scripts/inspect_sar_bands.py
```

Check each script's source and input/output paths before running it. Some scripts may expect files that are not included in the repository.

## Dataset and Caption Metadata

The master CSV is:

`metadata/caption_dataset_master.csv`

It records patch identifiers, city, SAR and optical file paths, image dimensions, band information, CRS, caption fields, verification status, reviewer notes, and data split information.

The inventory CSVs provide patch-level information for Goa and Mumbai.

## Data Storage

Large GeoTIFFs and patch files are excluded from ordinary Git tracking to keep the code repository manageable. Use an approved storage location or Git Large File Storage (Git LFS), after checking file sizes, storage limits, and data-source licence conditions.

Do not commit virtual environments, credentials, or unrelated backup copies.

## Research Notes

Optical images can assist with interpreting corresponding locations and preparing candidate descriptions. They should not automatically be treated as definitive ground truth for SAR imagery. Captions should be reviewed for features that can actually be supported by the SAR data.

This repository represents an evolving research prototype. Model training, evaluation, and VQA experiments should be documented as they are implemented.

## Acknowledgements

This project is intended for academic research and learning. Cite the original satellite data providers, research papers, and software used in any resulting reports or publications.
<<<<<<< HEAD
'@ | Set-Content -Encoding utf8 README.md
=======
>>>>>>> 363deec (Add project README and Python requirements)
