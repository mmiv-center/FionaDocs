# Changelog

Daily log of work, grouped by task.

## 2026-10-01

- Documentation: Agreed rule: every new feature is described in all 3 sections (User, SystemAdmin, Developer), each from a different angle and with a different level of detail.
- Developer: Added `pullStudyFromIDS7.sh` to the list of files. Added the docstring to the server script and the entry to `setup.sh`.
- End User: Added the "Application user guides" chapter. Moved the detailed Duplicate instructions to `EndUser/guides/duplicate.rst`; the Duplicate entry in "Specialized applications" now has only the short text from the About panel (with "Export permission") and a link to the guide.
- Landing page: Added the Duplicate tile (purple `#6a3d9a`, leaf05) and changed the layout to columns: data in under Assign (Attach, Migrate), data out under Export (NoAssign, Duplicate). Rows below Assign/Export are lower. Deployed to the server as `index.php`.
- End User: Added the Duplicate banner (`_static/duplicate.png`, a screenshot of the new landing page tile) to "Specialized applications".
- End User: Replaced the NoAssign, Attach and Review Meta-Data banners with screenshots of the new landing page.
