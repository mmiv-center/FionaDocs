#!/usr/bin/env bash

# Create the symbolic links to all the scripts (required to make html).


#if [ ! -e storectl.sh ]; then
#  ln -s /var/www/html/server/bin/storectl.sh storectl.sh
#fi

echo
echo "Create sybolic links to Fiona scripts (sh, py, php)..."
echo

# /home/processing/bin
files=("anonymizeAndSend.py"
  "clearExport.sh"
  "clearOldFiles.sh"
  "clearStaleLinks.sh"
  "createTransferRequestsForProcessed.py"
  "createTransferRequests.py"
  "populateAutoID.py"
  "populateIncoming.py"
  "populateProjects.py");

for file in "${files[@]}"; do
  if [[ ! -e "$file" ]]; then
    # ln -s /home/processing/bin/$file $file
    echo "*** $file: link created"
  else
    echo "*** $file: link exists"
  fi
done


# /home/processing/bin/utils
files=("getAllPatients2.sh"
  "parseAllPatients.sh"
  "resendProject.py"
  "whatIsInIDS7.py"
  "whatIsNotInIDS7.py");

for file in "${files[@]}"; do
  if [[ ! -e "$file" ]]; then
    # ln -s /home/processing/bin/utils/$file $file
    echo "*** $file: link created"
  else
    echo "*** $file: link exists"
  fi


echo
echo "Links created..."
echo



#if [ ! -e storectl.sh ]; then
#  ln -s /var/www/html/server/bin/storectl.sh storectl.sh
#  echo "Created link to: storectl.sh"
#fi


