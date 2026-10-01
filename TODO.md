# TODO

## Open

### Escape `*` in script docstrings
- **Problem:** The docstrings of `anonymizeAndSend.py` and `createTransferRequests.py` on the Fiona server contain `/data/site/raw/*/*/*.json`. In reStructuredText a bare `*` starts emphasis, so the path can render wrongly or raise *"Inline emphasis start-string without end-string"*. Older copies had `\*`, but the escapes are gone in the server version (checked 2026-09-24).
- **Fix:** Change the docstrings in the scripts **on the Fiona server** (not in local copies, which are overwritten), for example ``` ``/data/site/raw/*/*/*.json`` ```. Then check the other script docstrings for the same issue.
- **Files:** `anonymizeAndSend.py`, `createTransferRequests.py` (source: `/home/processing/bin/`)

### `setup.sh`: detect the Fiona version automatically
- **Problem:** `source/Developer/scripts/setup.sh` sets `FIONA_VERSION` by hand (now `fiona_v20260518`, used for all versioned paths). It must be updated after every Fiona upgrade, or the application scripts are skipped or linked to an old version.
- **Fix:** Read the version from `/data/config/config.json` (`jq -r .fiona_version`), the same way the new `storectl.sh` wrapper does. Build all versioned paths from it (`/var/www/html/fiona_v${fiona_version}/...`). Stop with a clear error if the key is missing or the directory does not exist.
- **Also:** Replace the five copy-pasted loops with one function, and link the real `storectl.sh` (see below).

### Two `storectl.sh` scripts on the Fiona server
- **Facts (confirmed on the server, 2026-09-24):**
  - `/var/www/html/server/bin/storectl.sh`: a small wrapper that reads `fiona_version` from `/data/config/config.json` and runs the versioned script.
  - `/var/www/html/fiona_v<version>/server/bin/storectl.sh`: the real script that starts and stops the DICOM receiver (`storescpd`).
- **To do:**
  - Document the **real** script in `scripts/storectl.rst`, and mention that the wrapper exists and what it does.
  - Update `setup.sh` so that it links the real script.
  - Update the folder tree in `Developer/developer-index.rst` (HTML and LaTeX versions) to show both locations.
  - Check whether the other `server/bin` scripts (`detectStudyArrival.sh`, `heartbeat.sh`, `processSingleFile3.py`, `sendFiles.sh`) and `server/utils/s2m.sh` also have newer copies under `fiona_v<version>/server/`, and document the right ones.

### Server script `setup-kopiowanie-skryptow-do-home.sh`
- **Context:** This helper script on the Fiona server copies all documented scripts to the home directory and packs them into a zip file. The zip is used to move the scripts to a workstation that has no access to the server.
- **To do:** Apply the same changes as in `setup.sh`: detect the Fiona version from `/data/config/config.json`, and copy the real `storectl.sh`, not the wrapper. Keep its list of scripts in sync with `setup.sh`, and ideally make both scripts use one shared list.
- **Note:** This script is not in this repository. Consider adding it next to `setup.sh` (for example as `source/Developer/scripts/pack-scripts.sh`) so that both are versioned together.

### Verify glossary entries
- **Problem:** Some glossary definitions are based on context only and are not confirmed.
- **To check:** DMA (expansion of "Sectra DMA Forskning"), EK (Elektronisk kvalitetshåndbok?), CDRobot (writes studies to CD/DVD?), OneConnect (PACS-to-PACS sharing with other institutions?).
- **Files:** `source/glossary.rst`

### Refresh landing page banners
- **Problem:** The landing page layout changed (2026-10-01): rows 2–4 are lower, and Migrate moved. The banners of Attach, NoAssign, Trace and Review in `_static/` still show the old, taller tiles.
- **Fix:** Take new screenshots while logged out, crop them to the tile and save them with 144 DPI (otherwise they are too wide in the PDF).
- **Files:** `source/_static/attach.png`, `noassign.png`, `review-meta-data.png`, `review-zip-file.jpeg`, and others if needed

## Done

### Duplicate: add application logo (2026-10-01)
- **Result:** New Duplicate tile on the landing page; its screenshot is `_static/duplicate.png` (144 DPI) and is shown in "Specialized applications".

### Document `pullStudyFromIDS7.sh` (2026-10-01)
- **Result:** Docstring added on the Fiona server; `scripts/pullStudyFromIDS7.rst`, Components entry, HTML and LaTeX tree branches, LaTeX toctree and `setup.sh` entry added.

### Check what the web server exposes from FionaDocs (2026-09-29)
- **Result:** The symlink `/var/www/html/fiona_v20260518/applications/FionaDocs` points to `/home/kocmar/FionaDocs/build/html`, so only the HTML output is served; `.git/`, `.venv/`, `source/` and the scripts are not exposed.
- **Consequence:** `build/latex/` is not reachable from the web. `make docs` now copies `fiona.pdf` into `build/html/` for the "Download PDF" button.
