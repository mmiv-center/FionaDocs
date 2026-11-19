# Changelog

Daily log of work, grouped by task.

## 2026-11-19

- End User: Export guide (`guides/export.rst`), "Secure download (email)": several recipients can now be separated with a semicolon (;) or a comma (,). The note now says that if any address is not from @helse-bergen.no or @ihelse.net, no e-mail is sent to any recipient. This follows the change in `createZipFileCmd.php`, which now checks every address, not only the last one.
- End User: The e-mail sent by `createZipFileCmd.php` now says "7 days", so the screenshot `export-email-3.png` matches the real e-mail.
- End User: Export guide (`guides/export.rst`), new section "Search and filters" before "Secure download (email)". It describes the search field (not case sensitive, `*` means "anything", regular expressions, the list updates while you type), the four filter groups (Events, Modalities, Actions, ZIP File Size) and how they are combined (OR inside a group, AND between groups and the search text). Two screenshots with fictional demo data, the important element marked in orange: `export-search-1.png` (search field) and `export-search-2.png` (open "Filters" menu).

## 2026-11-17

- End User: New guide "Export" (`guides/export.rst`) with the section "Secure download (email)". It describes how to send a study as a password-protected 7z archive to one or more e-mail addresses (separated by `;`, only `@helse-bergen.no` and `@ihelse.net`), the two e-mails (link, then password), the 7-day link and the need for a 7z program. Four screenshots with fictional demo data, the important element marked in orange: `export-email-1.png` (row menu), `export-email-2.png` (window "Secure download link"), `export-email-3.png` (first e-mail with the link) and `export-email-4.png` (second e-mail with the password). The Export section links to the guide.
- End User: The screenshot `export-email-3.png` shows "7 days". The e-mail sent by `createZipFileCmd.php` still says "a limited number of days".
- End User: The table of contents (HTML sidebar and PDF bookmarks) shows only the guide titles "Duplicate", "Attach PDF/JPG" and "Export" with "Secure download (email)", without their subsections (Access, Steps, Result etc.). Each guide file sets `:tocdepth:` for HTML and `\sphinxsetup{bookmarksdepth=...}` for PDF; at the end of the file the PDF bookmark depth is set back to 5.
- End User: The Attach guide (`guides/attach-pdf.rst`) now has the title "Attach" with the section "Attach PDF/JPG", the same structure as the Export guide, because attaching a PDF or JPEG is only one of the options of the Attach application. The link in the Attach section still shows "Attach PDF/JPG".

## 2026-11-13

- End User: New guide "Attach PDF" (`guides/attach-pdf.rst`) with three screenshots: `attach-pdf-1.png` (Attach page, fictional demo data), `attach-pdf-2.png` (window "Attach PDF/image to study") and `attach-pdf-3.png` (Patient History in the research PACS), both from the Demo test project; in `attach-pdf-3.png` the attached PDF and JPG images are marked in orange. It describes how to attach a PDF report or a JPEG image to an existing study in the research PACS, without Assign. The Attach section links to the guide.
- End User: The guide follows the new GUI texts: title "Attach PDF/JPG", button "Import PDF/JPG", window "Attach PDF/JPG to study". New screenshots `attach-pdf-1.png` and `attach-pdf-2.png` with these texts.

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
