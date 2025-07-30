#!/usr/bin/env bash

# Create the symbolic links to all the scripts (required to make html).


#if [ ! -e storectl.sh ]; then
#  ln -s /var/www/html/server/bin/storectl.sh storectl.sh
#fi



# /home/processing/bin
files = ("anonymizeAndSend.py"
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
    # create symbolic link
    # ln - /home/processing/bin/$file $file
    echo "$file: create link"
  else
    echo "$file: link exists"
  fi
done







#if [ ! -e storectl.sh ]; then
#  ln -s /var/www/html/server/bin/storectl.sh storectl.sh
#  echo "Created link to: storectl.sh"
#fi


