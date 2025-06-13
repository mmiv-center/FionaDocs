#!/usr/bin/env python3

from pathlib import Path

def extract_script_paths(input_file):
    """Extract script paths from the input file.
       
    Cretaded: 2025.06.12
    Updated: 2025.06.12
    """

    script_paths = []
    # valid extensions = currently only for .sh for shell scripts
    # We assume docstings start with: ["#", "##", "#:"]
    # To do: add *.php, *.python.
    valid_extensions = ('.sh')
    
    # Read file line by line
    with open(input_file, 'r') as f:
        for line in f:
            # Split line into parts
            words = line.split()
            
            # Check each part
            for word in words:
                # Check if part ends with valid extension
                if word.endswith(valid_extensions):
                    # Remove quotes
                    clean_path = word.strip('"\'')
                    script_paths.append(clean_path)
    
    # Remove duplicates using set()
    unique_paths = list(set(script_paths))
    
    # Save results to file
    output_file = 'scripts_extracted_from_crontab.txt'
    with open(output_file, 'w') as f:
        for path in unique_paths:
            f.write(f"{path}\n")
    
    print(f"Found {len(unique_paths)} unique script paths.")
    print(f"Results saved to file: {output_file}")

if __name__ == "__main__":
    # txt file created manually from crontab -l
    # crontab -l > processing-crontable-list.txt
    input_file = "processing-crontable-list.txt" 
    extract_script_paths(input_file)
    
