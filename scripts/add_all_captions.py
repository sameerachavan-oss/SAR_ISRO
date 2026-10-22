"""
Populate caption_verified for the 220 SAR/optical patch records.
Run from the SAR_ISRO project root:
    python scripts/add_all_captions.py

Captions are based on the supplied low-resolution contact sheets. They are
descriptive visual captions, not ground-truth land-use labels. Records with
unusual/false-colour optical previews are described conservatively.
The script creates a timestamped backup and preserves all other columns.
"""
from pathlib import Path
from datetime import datetime
import pandas as pd

CSV_PATH = Path("metadata/caption_dataset_master.csv")
if not CSV_PATH.exists():
    raise FileNotFoundError(f"Could not find {CSV_PATH}. Run this from the SAR_ISRO project root.")

GOA_CAPTIONS = {
    "GOA_000001": 'A coastal scene with open seawater along a narrow developed shoreline.',
    "GOA_000002": 'A mixed landscape of dense settlement, cultivated plots, and surrounding vegetation.',
    "GOA_000003": 'A patchwork of cultivated fields, scattered buildings, and a large vegetated area.',
    "GOA_000004": 'Built-up areas and cultivated plots bordering a broad vegetated tract.',
    "GOA_000005": 'A transition zone of cultivated land, vegetation, and scattered development.',
    "GOA_000006": 'A densely built-up area crossed by a prominent straight transport corridor.',
    "GOA_000007": 'Settlements and cultivated land beside a winding water channel.',
    "GOA_000008": 'Green cultivated plots and vegetation bordering a winding water channel.',
    "GOA_000009": 'A predominantly vegetated landscape with scattered development and a winding channel.',
    "GOA_000010": 'A broad meandering waterway with branching channels and adjacent vegetation.',
    "GOA_000011": 'A coastal waterway with enclosed water bodies, vegetation, and scattered development.',
    "GOA_000012": 'Open seawater beside a narrow shoreline and dense coastal development.',
    "GOA_000013": 'A mixed landscape of built-up areas, vegetation, cultivated fields, and open plots.',
    "GOA_000014": 'Developed areas and vegetation surrounding a winding water channel.',
    "GOA_000015": 'A mixed landscape of developed areas, vegetation, and open terrain.',
    "GOA_000016": 'Patchwork cultivated plots and vegetation interspersed with scattered buildings.',
    "GOA_000017": 'A densely developed landscape crossed by a prominent transport corridor.',
    "GOA_000018": 'A mixed landscape of scattered development, vegetation, and open land.',
    "GOA_000019": 'Cultivated plots and vegetation beside a winding waterway.',
    "GOA_000020": 'Vegetated land and cultivated areas bordering a broad curving waterway.',
    "GOA_000021": 'A winding waterway bordered by vegetation, open land, and built-up areas.',
    "GOA_000022": 'Branching water channels among vegetation and developed land.',
    "GOA_000023": 'Open seawater beside a developed coastal strip.',
    "GOA_000024": 'Open seawater, a curving shoreline, built-up areas, and vegetation.',
    "GOA_000025": 'Built-up areas and vegetation surrounding a winding water channel.',
    "GOA_000026": 'A winding waterway bordered by vegetation, open plots, and settlements.',
    "GOA_000027": 'Open seawater beside a developed shoreline with patches of vegetation.',
    "GOA_000028": 'A developed coastal area beside open water.',
    "GOA_000029": 'Coastal built-up land bordering open water and vegetation.',
    "GOA_000030": 'A coastal inlet bordered by built-up areas and vegetation.',
    "GOA_000031": 'A broad vegetated area beside open water and a curving shoreline.',
    "GOA_000032": 'A coastal waterway bordered by vegetation, open water, and development.',
    "GOA_000033": 'A winding channel separating vegetated land from developed areas and open plots.',
    "GOA_000034": 'Open seawater beside a narrow developed shoreline.',
    "GOA_000035": 'A curving shoreline with built-up areas, vegetation, and a waterway.',
    "GOA_000036": 'A coastal landscape containing a waterway, cultivated plots, vegetation, and development.',
    "GOA_000037": 'Open water, a coastal shoreline, vegetation, and built-up areas.',
    "GOA_000038": 'Developed coastal land surrounding a curved water inlet.',
    "GOA_000039": 'A coastal urban area surrounding a broad water inlet.',
    "GOA_000040": 'A developed coastal landscape with a waterway and a prominent crossing.',
    "GOA_000041": 'A broad waterway bordered by vegetation, developed areas, and open terrain.',
    "GOA_000042": 'A coastal waterway separating vegetated land from development and transport routes.',
    "GOA_000043": 'A branching waterway surrounded by vegetation, open land, and scattered buildings.',
    "GOA_000044": 'A broad waterway bordered by vegetation, cultivated plots, and developed land.',
    "GOA_000045": 'Open seawater beside a developed shoreline.',
    "GOA_000046": 'A coastal peninsula with built-up areas and vegetation surrounded by open seawater.',
    "GOA_000047": 'A curved coastline with open seawater and developed land.',
    "GOA_000048": 'A coastal inlet bordered by built-up areas, vegetation, and open seawater.',
    "GOA_000049": 'Developed coastal land bordering open water.',
    "GOA_000050": 'A developed coastal area directly beside open water.',
    "GOA_000051": 'A developed landscape with transport routes, vegetation, and a winding waterway.',
    "GOA_000052": 'A mixed landscape of development, open plots, vegetation, and intersecting transport routes.',
    "GOA_000053": 'Built-up areas, open plots, vegetation, and a winding water channel.',
    "GOA_000054": 'A mixed urban and vegetated landscape with open plots and a curving waterway.',
    "GOA_000055": 'A developed landscape with a curving transport route, vegetation, and open land.',
    "GOA_000056": 'Open water with a small coastal landform at the edge of the image.',
    "GOA_000057": 'Open water and a small coastal landform, with little visible built-up land.',
    "GOA_000058": 'Open water dominating the scene, with a narrow coastal feature near the edge.',
    "GOA_000059": 'Mostly open water with a small shoreline feature near the image boundary.',
    "GOA_000060": 'Open water adjoining a narrow sandy or developed shoreline.',
    "GOA_000061": 'A coastal settlement and cultivated plots beside open seawater.',
    "GOA_000062": 'A developed coastal area with open water, vegetation, and cultivated plots.',
    "GOA_000063": 'A mixed coastal landscape with settlement, fields, vegetation, and open water.',
    "GOA_000064": 'A developed landscape with cultivated plots and a broad vegetated area.',
    "GOA_000065": 'Scattered settlements and cultivated plots bordering dense vegetation.',
    "GOA_000066": 'Built-up areas and open plots interspersed with vegetation.',
    "GOA_000067": 'A vegetated landscape with scattered settlements and open land.',
    "GOA_000068": 'A mixed landscape of dense settlement, vegetation, and cultivated plots.',
    "GOA_000069": 'An open-water scene with no clearly distinguishable land features in the preview.',
    "GOA_000070": 'An open-water scene with a small bright coastal feature near the edge.',
    "GOA_000071": 'Mostly open water with a narrow coastal feature at the image boundary.',
    "GOA_000072": 'Open seawater adjoining a curved developed shoreline.',
    "GOA_000073": 'Open water and a curving shoreline with adjacent settlement and fields.',
    "GOA_000074": 'A coastal bay with a curved shoreline and nearby developed land.',
    "GOA_000075": 'A developed coastal strip beside a broad bay.',
    "GOA_000076": 'A coastal settlement along a curved shoreline with open water.',
    "GOA_000077": 'A coastal urban area with roads, buildings, and nearby open water.',
    "GOA_000078": 'A developed landscape crossed by a curving road and surrounded by vegetation.',
    "GOA_000079": 'A mixed settlement and vegetated landscape with a prominent curving road.',
    "GOA_000080": 'Scattered development and vegetation around open plots and winding drainage features.',
    "GOA_000081": 'A mixed landscape of settlement, vegetation, and open terrain.',
    "GOA_000082": 'A developed area with a winding road and patches of vegetation.',
    "GOA_000083": 'A mixed landscape of built-up areas, open land, and vegetation.',
    "GOA_000084": 'A developed landscape with a prominent curving road and open plots.',
    "GOA_000085": 'A coastal settlement with a curved shoreline and adjoining open water.',
    "GOA_000086": 'A developed coastal landscape with buildings, roads, and patches of vegetation.',
    "GOA_000087": 'A coastal settlement and transport routes beside open water.',
    "GOA_000088": 'A coastal landscape with a developed shoreline and adjacent vegetation.',
    "GOA_000089": 'A developed coastal area with a curved shoreline and open water.',
    "GOA_000090": 'A coastal settlement with roads and open water along the image edge.',
    "GOA_000091": 'A developed coastal landscape with a narrow inlet and surrounding vegetation.',
    "GOA_000092": 'A mixed coastal landscape of settlements, open plots, and water channels.',
    "GOA_000093": 'A developed coastal area with a curving shoreline and open water.',
    "GOA_000094": 'A coastal settlement bordering a bay, with roads and vegetation.',
    "GOA_000095": 'A coastal scene with a developed peninsula and open seawater.',
    "GOA_000096": 'A developed coastal landscape with a curved shoreline and transport routes.',
    "GOA_000097": 'A coastal settlement with a water channel and patches of vegetation.',
    "GOA_000098": 'A coastal landscape with built-up areas, a curving road, and open water.',
    "GOA_000099": 'A developed coastal area with a curved shoreline and water channel.',
    "GOA_000100": 'A coastal settlement with open water and adjacent vegetation.',
    "GOA_000101": 'A coastal landscape with a curved shoreline, buildings, and transport routes.',
    "GOA_000102": 'A coastal landscape with built-up land, vegetation, and a water channel.',
    "GOA_000103": 'A developed coastal area with a road following the shoreline.',
    "GOA_000104": 'A coastal settlement and transport routes beside open water.',
    "GOA_000105": 'A developed coastal landscape with a shoreline and patches of vegetation.',
    "GOA_000106": 'A coastal landscape with open water and a developed point of land.',
    "GOA_000107": 'A developed coastal area with a curved shoreline and nearby vegetation.',
    "GOA_000108": 'A coastal settlement with open water, roads, and scattered green plots.',
    "GOA_000109": 'A developed coastal landscape with open water and a narrow shoreline.',
    "GOA_000110": 'A coastal scene with open water and a developed shoreline.',
}

MUMBAI_CAPTIONS = {
    "MUMBAI_000001": 'Mostly open water with a small coastal feature visible near the lower edge.',
    "MUMBAI_000002": 'Open water beside a narrow developed shoreline.',
    "MUMBAI_000003": 'A dense coastal urban area adjoining a water body.',
    "MUMBAI_000004": 'Dense built-up urban blocks with roads and small open plots.',
    "MUMBAI_000005": 'A dense urban landscape of buildings, roads, and industrial-looking roofs.',
    "MUMBAI_000006": 'A built-up urban area crossed by major roads and transport corridors.',
    "MUMBAI_000007": 'Dense development beside a winding water channel and vegetated land.',
    "MUMBAI_000008": 'Large light-roofed structures beside a broad vegetated area and water channel.',
    "MUMBAI_000009": 'Dense urban blocks bordering a vegetated tract and water channel.',
    "MUMBAI_000010": 'A dense urban and industrial landscape with large tanks or circular roof structures.',
    "MUMBAI_000011": 'Mostly open water with a narrow coastal strip visible at the edge.',
    "MUMBAI_000012": 'Open water beside a narrow developed shoreline.',
    "MUMBAI_000013": 'A coastal urban strip with dense buildings beside open water.',
    "MUMBAI_000014": 'Dense built-up blocks with roads and scattered larger roof structures.',
    "MUMBAI_000015": 'A dense urban landscape with tightly packed buildings and road corridors.',
    "MUMBAI_000016": 'Dense urban development crossed by intersecting roads.',
    "MUMBAI_000017": 'A developed coastal area beside a broad water body and curved shoreline.',
    "MUMBAI_000018": 'Open water and a broad pale-toned surface crossed by a linear transport route.',
    "MUMBAI_000019": 'A broad pale-toned surface with vegetation and a road, adjoining developed land.',
    "MUMBAI_000020": 'An urban-industrial area with large roof structures, roads, and adjacent open land.',
    "MUMBAI_000021": 'Mostly open water with little clearly visible land in the preview.',
    "MUMBAI_000022": 'Open water beside a narrow developed coastal strip.',
    "MUMBAI_000023": 'A coastal urban area with dense buildings along a curving shoreline.',
    "MUMBAI_000024": 'A dense urban landscape with a large oval sports ground and surrounding buildings.',
    "MUMBAI_000025": 'A dense urban landscape with major roads and tightly packed buildings.',
    "MUMBAI_000026": 'A developed coastal edge with dense buildings beside open water.',
    "MUMBAI_000027": 'Open water beside a developed coastal edge.',
    "MUMBAI_000028": 'A pale-toned open area crossed by a straight road and bordered by development.',
    "MUMBAI_000029": 'A pale-toned open area with a diagonal road and sparse visible structures.',
    "MUMBAI_000030": 'A pale-toned open area with roads and a few large geometric structures.',
    "MUMBAI_000031": 'Mostly open water with a narrow shoreline feature at the edge.',
    "MUMBAI_000032": 'A coastal urban area with dense buildings beside open water.',
    "MUMBAI_000033": 'Dense built-up blocks along a curved coastal shoreline.',
    "MUMBAI_000034": 'A dense urban landscape with an oval sports ground and surrounding development.',
    "MUMBAI_000035": 'Dense urban blocks with major roads and a large transport corridor.',
    "MUMBAI_000036": 'A coastal industrial area with large structures and adjoining open water.',
    "MUMBAI_000037": 'Open water beside a developed coastal edge.',
    "MUMBAI_000038": 'A mostly pale-toned surface with indistinct texture and few clear land features.',
    "MUMBAI_000039": 'A mostly pale-toned surface with broad textured patterns and no confidently identifiable land use.',
    "MUMBAI_000040": 'A mostly pale-toned surface with mixed broad texture and indistinct features.',
    "MUMBAI_000041": 'Open water adjoining a narrow developed shoreline.',
    "MUMBAI_000042": 'A coastal urban landscape with dense buildings and open water.',
    "MUMBAI_000043": 'Dense urban blocks and roads near a curved shoreline.',
    "MUMBAI_000044": 'A dense urban landscape with roads and tightly packed buildings.',
    "MUMBAI_000045": 'A dense urban landscape with major road corridors and built-up blocks.',
    "MUMBAI_000046": 'A coastal urban area with industrial-looking structures beside open water.',
    "MUMBAI_000047": 'A mostly pale-toned surface with broad textured patterns.',
    "MUMBAI_000048": 'A mostly pale-toned surface with broad textured patterns and a bright linear feature.',
    "MUMBAI_000049": 'Mostly open water with a small bright structure and a narrow access route.',
    "MUMBAI_000050": 'Open water surrounding a small bright structure linked by a narrow route.',
    "MUMBAI_000051": 'A narrow developed coastal strip extending into open water.',
    "MUMBAI_000052": 'A coastal peninsula with dense buildings and a curved shoreline.',
    "MUMBAI_000053": 'A coastal settlement with dense buildings beside a curved bay.',
    "MUMBAI_000054": 'Dense urban blocks beside a curved shoreline and open water.',
    "MUMBAI_000055": 'A dense urban landscape with roads and built-up blocks beside water.',
    "MUMBAI_000056": 'A developed coastal landscape with a port-like waterfront and open water.',
    "MUMBAI_000057": 'A coastal industrial area with large structures beside open water.',
    "MUMBAI_000058": 'A mostly pale-toned textured surface with indistinct broad patterns.',
    "MUMBAI_000059": 'A mostly pale-toned surface with irregular broad texture.',
    "MUMBAI_000060": 'A mostly pale-toned surface with broad textured patterns and no clear land-cover boundaries.',
    "MUMBAI_000061": 'A mostly pale-toned surface with broad texture and a narrow bright linear feature.',
    "MUMBAI_000062": 'A coastal urban area with a narrow shoreline and open water.',
    "MUMBAI_000063": 'A broad open-water area with a small developed point of land.',
    "MUMBAI_000064": 'Open water beside a narrow developed coastal strip.',
    "MUMBAI_000065": 'A curved bay bordered by a dense developed shoreline.',
    "MUMBAI_000066": 'A dense coastal urban area beside a curved bay.',
    "MUMBAI_000067": 'A dense urban and industrial landscape with large roofs and transport corridors.',
    "MUMBAI_000068": 'A coastal industrial area with large structures and open water.',
    "MUMBAI_000069": 'A mostly open-water scene with a small bright structure and access route.',
    "MUMBAI_000070": 'A mostly open-water scene with a long narrow bright access route.',
    "MUMBAI_000071": 'A mostly pale-toned surface with a prominent straight linear feature.',
    "MUMBAI_000072": 'A mostly pale-toned surface with broad texture and a bright linear corridor.',
    "MUMBAI_000073": 'A mostly pale-toned surface with a small bright feature and diffuse texture.',
    "MUMBAI_000074": 'A mostly pale-toned surface with broad texture and a narrow linear feature.',
    "MUMBAI_000075": 'A mostly open-water scene with a small bright structure near the edge.',
    "MUMBAI_000076": 'A coastal urban landscape with dense buildings and a curved shoreline.',
    "MUMBAI_000077": 'A coastal settlement with a narrow developed strip beside open water.',
    "MUMBAI_000078": 'A coastal urban area with a broad water body and a curved shoreline.',
    "MUMBAI_000079": 'A dense urban waterfront with closely spaced buildings and roads.',
    "MUMBAI_000080": 'A dense urban area with a major road corridor and industrial-looking roofs.',
    "MUMBAI_000081": 'A dense urban waterfront with piers or projecting structures along the coast.',
    "MUMBAI_000082": 'Open water beside a narrow developed coastal strip.',
    "MUMBAI_000083": 'A coastal urban landscape with a curved shoreline and dense buildings.',
    "MUMBAI_000084": 'A dense urban landscape with roads and closely spaced blocks.',
    "MUMBAI_000085": 'A dense coastal urban area with a port-like waterfront.',
    "MUMBAI_000086": 'A coastal industrial landscape with large structures beside open water.',
    "MUMBAI_000087": 'A coastal urban area with dense buildings and a curved shoreline.',
    "MUMBAI_000088": 'Open water with a small bright vessel-like feature.',
    "MUMBAI_000089": 'A coastal urban landscape with a curved developed shoreline.',
    "MUMBAI_000090": 'A coastal urban area with dense buildings and a narrow water channel.',
    "MUMBAI_000091": 'Open water with a developed point of land extending into the water.',
    "MUMBAI_000092": "A coastal urban landscape with dense buildings along the water's edge.",
    "MUMBAI_000093": 'A coastal settlement beside a broad water body.',
    "MUMBAI_000094": 'A mostly pale-toned surface with broad textured patterns.',
    "MUMBAI_000095": 'A mostly pale-toned surface with diffuse patterns and indistinct land features.',
    "MUMBAI_000096": 'A mostly pale-toned surface with broad textured patterns and a few bright spots.',
    "MUMBAI_000097": 'A mostly pale-toned surface with diagonal texture and indistinct features.',
    "MUMBAI_000098": 'A coastal urban area with a narrow developed shoreline and open water.',
    "MUMBAI_000099": 'A coastal urban landscape with dense buildings beside open water.',
    "MUMBAI_000100": 'Open water beside a small developed peninsula.',
    "MUMBAI_000101": 'A coastal urban area with a developed point of land surrounded by water.',
    "MUMBAI_000102": 'A coastal urban area with a narrow developed shoreline and open water.',
    "MUMBAI_000103": 'A mostly pale-toned surface with broad texture and a bright coastal edge.',
    "MUMBAI_000104": 'A mostly open-water scene with a developed shoreline along one edge.',
    "MUMBAI_000105": 'A coastal urban area with dense buildings along a curved shoreline.',
    "MUMBAI_000106": 'A coastal scene with a developed point of land surrounded by open water.',
    "MUMBAI_000107": 'A coastal urban landscape with dense buildings and open water.',
    "MUMBAI_000108": 'Open water adjoining a narrow developed coastal strip.',
    "MUMBAI_000109": 'Open water beside a narrow developed shoreline and coastal structures.',
    "MUMBAI_000110": 'A coastal urban landscape with dense buildings along the edge of open water.',
}

CAPTIONS = {**GOA_CAPTIONS, **MUMBAI_CAPTIONS}
df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)

required = {"patch_id", "caption_verified", "verification_status"}
missing_cols = required - set(df.columns)
if missing_cols:
    raise ValueError(f"CSV is missing required columns: {sorted(missing_cols)}")

if df["patch_id"].duplicated().any():
    dupes = df.loc[df["patch_id"].duplicated(keep=False), "patch_id"].tolist()
    raise ValueError(f"Duplicate patch_id values found: {dupes[:20]}")

missing_ids = sorted(set(CAPTIONS) - set(df["patch_id"]))
if missing_ids:
    raise ValueError(f"These expected patch IDs are missing from CSV: {missing_ids[:20]}")

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_path = CSV_PATH.with_name(f"caption_dataset_master_before_all_captions_{stamp}.csv")
df.to_csv(backup_path, index=False, encoding="utf-8-sig")

for patch_id, caption in CAPTIONS.items():
    row_index = df.index[df["patch_id"].eq(patch_id)][0]
    df.at[row_index, "caption_verified"] = caption
    df.at[row_index, "verification_status"] = "reviewed_contact_sheet"

caption_map = df.set_index("patch_id")["caption_verified"].to_dict()
bad = [pid for pid, cap in CAPTIONS.items() if caption_map.get(pid, "").strip() != cap]
if bad:
    raise ValueError(f"Caption validation failed for: {bad[:20]}")

df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
print("SUCCESS: captioned all 220 patches.")
print(f"Goa captions: {len(GOA_CAPTIONS)}")
print(f"Mumbai captions: {len(MUMBAI_CAPTIONS)}")
print(f"Non-empty caption_verified values: {sum(bool(x.strip()) for x in df['caption_verified'])}")
print(f"Backup created: {backup_path}")
print(f"Updated dataset: {CSV_PATH}")
