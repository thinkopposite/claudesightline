# Sightline Schematic

Stadium seating bowl designer. Set the field, tiers and side-by-side stand profiles (NEZ/SEZ, East/West), and every riser is solved to your C-value. Exports straight to Revit (via Dynamo) and SketchUp.

**Open the app:** `https://<your-github-username>.github.io/<repo-name>/`

Sightline Schematic runs entirely in the browser. Nothing is uploaded, and there is no server or account. Saved options live in the browser you saved them in; use **Back up options** / **Restore options** to move them between computers.

## Revit

1. In Sightline, click **Export for Revit (.xlsx)**.
2. In Revit 2024: File > New > Family > `Metric Generic Model.rft`, save it.
3. Open Dynamo Player, run [`dynamo/Sightline_BowlMass_R2024.dyn`](dynamo/Sightline_BowlMass_R2024.dyn), pick the workbook.
4. Each stand is built on its own subcategory (`Sightline T1 NEZ`, `Sightline T2 E`, ...). Load the family into the project and place it at the project base point (origin = field centre at pitch level).

Base version: Revit 2024.0 / Dynamo 2.17 (CPython3). No packages needed. Keep this file as the master; a copy saved from Revit 2025+ won't open cleanly in 2024.

## SketchUp

**Export for SketchUp** downloads a ZIP with a COLLADA file. File > Import > COLLADA. Units are metres; each stand is its own solid.

## Files

| Path | What it is |
|---|---|
| `index.html` | The whole app |
| `vendor/` | SheetJS 0.18.5 and JSZip 3.10, bundled so the app works where CDNs are blocked |
| `dynamo/` | Revit 2024 Dynamo graph |
| `publish.py` | Publishes a new version to this repo (used when Claude updates the app) |

## Changes

- **2026.09.27** Bowl split into tiers x four sides with per-side profiles, bench seating, open corners where sides differ, guard and headroom checks, suite levels, per-stand Revit subcategories. Standalone web version with option backup.
- **2026.09.26** Focal path export; auto bowl-mass Dynamo graph.
