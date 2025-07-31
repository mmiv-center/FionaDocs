#!/usr/bin/env bash
# Create the symbolic links to all the scripts (required to make html).
#
# (C) mk & hb
#
# Created: 2025.07.28
# Updated: 2025.07.30
#
# Example test:
#   if [ ! -e storectl.sh ]; then
#     ln -s /var/www/html/server/bin/storectl.sh storectl.sh
#   fi

# Messages
MSG_HEADER="Creates symbolic links to Fiona scripts (sh, py, php)..."
MSG_FOOTER="All links created..."
MSG_SM_CREATED="symlink created..."
MSG_SM_EXISTS="...symlink exists"
MSG_FILE_EXISTS="...file exists (not a symlink)"

# --dry-run mode
DRY_RUN=false
if [[ "$1" == "--dry-run" ]]; then
    DRY_RUN=true
    echo "=== DRY RUN MODE ==="
fi

echo
echo "$MSG_HEADER"
echo

# /home/processing/bin
files1=("anonymizeAndSend.py"
  "clearExports.sh"
  "clearOldFiles.sh"
  "clearStaleLinks.sh"
  "createTransferRequestsForProcessed.py"
  "createTransferRequests.py"
  "populateAutoID.py"
  "populateIncoming.py"
  "populateProjects.py");

for file in "${files1[@]}"; do
  source_file="/home/processing/bin/$file"
  
  # Source file validation
  if [[ ! -e "$source_file" ]]; then
    echo "*** WARNING: Source file does not exist: $source_file"
    continue
  fi
  
  if [[ -L "$file" ]]; then
    echo "*** $file: $MSG_SM_EXISTS"
  elif [[ -e "$file" ]]; then
    echo "*** $file: $MSG_FILE_EXISTS"
  else
    if [[ "$DRY_RUN" == "true" ]]; then
       echo "*** [DRY-RUN] Would create: ln -s $source_file $file"
    else
        ln -s "$source_file" "$file"
    fi    
    echo "*** $file: $MSG_SM_CREATED"
  fi
done

# /home/processing/bin/utils
files2=("getAllPatients2.sh"
  "parseAllPatients.sh"
  "resendProject.py"
  "whatIsInIDS7.py"
  "whatIsNotInIDS7.py");

for file in "${files2[@]}"; do
  source_file="/home/processing/bin/utils/$file"
  
  # Source file validation
  if [[ ! -e "$source_file" ]]; then
    echo "*** WARNING: Source file does not exist: $source_file"
    continue
  fi
  
  if [[ -L "$file" ]]; then
    echo "*** $file: $MSG_SM_EXISTS"
  elif [[ -e "$file" ]]; then
    echo "*** $file: $MSG_FILE_EXISTS"
  else
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "*** [DRY-RUN] Would create: ln -s $source_file $file"
    else
        ln -s "$source_file" "$file"
    fi
    echo "*** $file: $MSG_SM_CREATED"
  fi
done

# /var/www/html/server/bin
files3=("detectStudyArrival.sh"
  "heartbeat.sh"
  "moveFromScanner.sh"
  "mppsctl.sh"
  "processSingleFile3.py"
  "sendFiles.sh"
  "storectl.sh");

for file in "${files3[@]}"; do
  source_file="/var/www/html/server/bin/$file"
  
  # Source file validation
  if [[ ! -e "$source_file" ]]; then
    echo "*** WARNING: Source file does not exist: $source_file"
    continue
  fi
  
  if [[ -L "$file" ]]; then
    echo "*** $file: $MSG_SM_EXISTS"
  elif [[ -e "$file" ]]; then
    echo "*** $file: $MSG_FILE_EXISTS"
  else
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "*** [DRY-RUN] Would create: ln -s $source_file $file"
    else
        ln -s "$source_file" "$file"
    fi
    echo "*** $file: $MSG_SM_CREATED"
  fi
done

# /var/www/html/applications
files4=("Assign/php/removeOldEntries.sh"
  "Attach/process_tiff.sh"
  "Exports/php/createZipFileCmd.php"
  "User/asttt/code/cron.sh"
  "Workflows/php/runOneJob.sh");

for file in "${files4[@]}"; do
  source_file="/var/www/html/applications/$file"
  # we need to extract only file name from the subpath
    filename="${file##*/}"
  
  # Source file validation
  if [[ ! -e "$source_file" ]]; then
    echo "*** WARNING: Source file does not exist: $source_file"
    continue
  fi
  
  if [[ -L "$filename" ]]; then
    echo "*** $filename: $MSG_SM_EXISTS"
  elif [[ -e "$filename" ]]; then
    echo "*** $filename: $MSG_FILE_EXISTS"
  else
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "*** [DRY-RUN] Would create: ln -s $source_file $filename"
    else
        ln -s "$source_file" "$filename"
    fi    
    echo "*** $file: $MSG_SM_CREATED"
  fi
done


# /var/www/html/server/utils
files5=("s2m.sh");

for file in "${files5[@]}"; do
  source_file="/var/www/html/server/utils/$file"
  
  # Source file validation
  if [[ ! -e "$source_file" ]]; then
    echo "*** WARNING: Source file does not exist: $source_file"
    continue
  fi
  
  if [[ -L "$file" ]]; then
    echo "*** $file: $MSG_SM_EXISTS"
  elif [[ -e "$file" ]]; then
    echo "*** $file: $MSG_FILE_EXISTS"
  else
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "*** [DRY-RUN] Would create: ln -s $source_file $file"
    else
        ln -s "$source_file" "$file"
    fi
    echo "*** $file: $MSG_SM_CREATED"
  fi
done




echo
echo "$MSG_FOOTER"
echo

#if [ ! -e storectl.sh ]; then
#  ln -s /var/www/html/server/bin/storectl.sh storectl.sh
#  echo "Created link to: storectl.sh"
#fi