sh/newStudyOnScanner.sh
=======================


MPPS generates a MPPS.* file in /data/scanner/MPPS.<study instance uid>
incron detects the new file and calls this script (newStudyOnScanner.sh).
This script will create a touch file in /data/active-scans/<study instance uid>
For each file in /data/active-scans/ we will try to pull images using movescu for
each series that does not exist already.

