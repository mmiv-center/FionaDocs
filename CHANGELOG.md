# Changelog

Daily log of work, grouped by task.

## 2026-11-13

- End User: New guide "Attach PDF" (`guides/attach-pdf.rst`) with two screenshots (`attach-pdf-1.png`, `attach-pdf-2.png`, fictional demo data). It describes how to attach a PDF report or a JPEG image to an existing study in the research PACS, without Assign. The Attach section links to the guide. The research PACS screenshot (`attach-pdf-3.png`) is still missing.

## 2026-10-22

- Exports: Jobs in `prepared_downloads_list.jobs` now always store the user under the key `user_name`. Before, the multi-row request (`appendToDownloadListMultiple.php`) wrote `user`, so such jobs had no user name in the `createZipFileCmd.php` log. Changed in `appendToDownloadListMultiple.php` on the server.
- Exports: Button colours are now refreshed every 2 seconds in both directions. Before, a button stayed green after its zip file was deleted. At the start of each refresh `updateNew()` in `all.js` sets all buttons back to blue `download`, then the refresh sets the current state. Changed in `all.js` on the server.

## 2026-10-13

- Exports: All export types now clear InstitutionAddress (0008,0081) and InstitutionalDepartmentName (0008,1040). Before, only the Transpara export cleared them. InstitutionName (0008,0080) is not changed, because it holds the project name. Changed in `createZipFileCmd.php` on the server.
- Fiona-Packager: The web package now includes the documentation. `applications/FionaDocs` is a symlink to `/home/kocmar/FionaDocs/build/html`, so it is added to `SOURCE_FILES_WEB` as `applications/FionaDocs/.`: the trailing `/.` makes tar pack the content behind this one link, not the link itself. Changed in the Makefile on the server, not tested yet.

## 2026-10-12

- Exports: Added a link to Duplicate under "Package destination". The help text is now "Select the destination of the package. To copy studies to another project instead, use Duplicate."

## 2026-10-01

- Documentation: Agreed rule: every new feature is described in all 3 sections (User, SystemAdmin, Developer), each from a different angle and with a different level of detail.
- Developer: Added `pullStudyFromIDS7.sh` to the list of files. Added the docstring to the server script and the entry to `setup.sh`.
- End User: Added the "Application user guides" chapter. Moved the detailed Duplicate instructions to `EndUser/guides/duplicate.rst`; the Duplicate entry in "Specialized applications" now has only the short text from the About panel (with "Export permission") and a link to the guide.
- Landing page: Added the Duplicate tile (purple `#6a3d9a`, leaf05) and changed the layout to columns: data in under Assign (Attach, Migrate), data out under Export (NoAssign, Duplicate). Rows below Assign/Export are lower. Deployed to the server as `index.php`.
- End User: Added the Duplicate banner (`_static/duplicate.png`, a screenshot of the new landing page tile) to "Specialized applications".
- End User: Replaced the NoAssign, Attach and Review Meta-Data banners with screenshots of the new landing page.
